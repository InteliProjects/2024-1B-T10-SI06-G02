from flask import Blueprint, jsonify, request, send_file
from services.helper_predict import predict
from datetime import datetime
import io
import pandas as pd
from services.DbContext import DbContext

predict_bp = Blueprint('predict_bp', __name__)



@predict_bp.route('/predict', methods=['POST'])
def prediction_route():
    """
    Rota para predição de sentimento
    
    Args:
        data (str): Comentário a ser analisado
        
    Returns:
        
        {
            "prediction": 1,
            "ultimas_24_horas": {
                "negatives": 50.0,
                "positives": 50.0
            },
            "date": "2021-07-07 19:00"
        }   
    """
    db = DbContext()
    try:
        data = request.json['data']
        predictions = predict(data)
        predictions_list = predictions.tolist()
        prediction = predictions_list[0]
        resposta = {
            'prediction': prediction,
            'ultimas_24_horas': db.positiveAndNegativeCount(1),
            'date': datetime.now()
        }
        
        db.addPrediction({
            'comment': data,
            'sentiment': prediction,
        })
        
        return jsonify(resposta)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@predict_bp.route('/csv', methods=['POST'])
async def prediction_route_csv():
    """
    Rota para predição de sentimento em lote
    
    Args:
        file (file): Arquivo CSV contendo os comentários a serem analisados
        
    Returns:
        CSV contendo os comentários e suas respectivas predições
    """
    db = DbContext()
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        file_stream = io.BytesIO(file.read())
        file_stream.seek(0)

        data = pd.read_csv(file_stream)

        # Extrair vetores das colunas apropriadas
        vectors = data.iloc[:, 2:].values.tolist()  # Supondo que os vetores comecem da terceira coluna

        # Realizar a predição
        predictions = predict(vectors)

        if predictions is None:
            return jsonify({'message': 'Erro na predição'}), 500

        # Montar os resultados das predições
        results = []
        for i in range(len(data)):
            
            results.append({
                'comment': data.iloc[i, 0],  # Assumindo que a primeira coluna contenha os comentários
                'sentiment': predictions[i]
            })

        # Salvar as predições no banco de dados
        if db.addPredictions(results):
            print("Predições salvas no banco de dados.")
        else:
            raise Exception("Erro ao salvar predições no banco de dados.")

        # Preparar o DataFrame de resposta
        response_data = pd.DataFrame(results)

        # Preparar o arquivo CSV de saída
        output = io.BytesIO()
        response_data.to_csv(output, index=False)
        output.seek(0)

        # Retornar o arquivo CSV como resposta
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='predictions.csv')
    except IndexError as e:
        return jsonify({'message': 'Erro no índice do arquivo CSV'}), 400
    except Exception as e:
        print("erro na rota: ",e)
        return jsonify({'message rota': str(e)})
