from flask import Flask, Blueprint, jsonify, request, send_file
import requests
import io
import pandas as pd


process_bp = Blueprint('process_bp', __name__)

@process_bp.route('/csv', methods=['POST'])
def process_csv():
    """

    Esta rota recebe um request POST com um payload JSON contendo o texto a ser processado.
    Retorna um payload JSON com a previsão.
    
    Exemplo de request:
    {
        "data": "Uber é um serviço incrível!"
    }
    
    Resposta:
    {
        "prediction": 1
    }
    
    """
    

    
    try:
        
        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        

        
        # Enviar solicitação para limpeza de dados enviando o csv
        request_clean = requests.post("http://localhost:5000/clean_data/csv", files={"file": (file.filename, file)})
        request_clean.raise_for_status()
        #salvar o arquivo limpo numa variavel
        cleaned_file = request_clean.content
        

        # Enviar solicitação para vetorização
        request_vetor = requests.post("http://localhost:5000/vectorize/csv", files={"file": ("cleaned_data.csv", cleaned_file)})
        request_vetor.raise_for_status()
        response_vetor = request_vetor.content

        # Enviar solicitação para previsão
        request_predict = requests.post("http://localhost:5000/predict/csv", files={"file": ("vetorized_data.csv", response_vetor)})
        request_predict.raise_for_status()
        response_predict = request_predict.content
        
        return send_file(io.BytesIO(response_predict), mimetype='text/csv', as_attachment=True, download_name='predictions.csv')
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
        
 