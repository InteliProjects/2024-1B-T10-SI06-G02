from flask import Flask, Blueprint, jsonify, request, send_file
import numpy as np
import io 
import pandas as pd
from services.helper_vetor import vectorize_text

vectorize_bp = Blueprint('vectorize_bp', __name__)


@vectorize_bp.route('/tweet', methods=['POST'])
def vectorize_text_route():
    """
    Esta rota recebe um request POST com um payload JSON contendo o texto a ser vetorizado.
    Retorna um payload JSON com o vetor.

    Exemplo de request:
    {
        "text": "Uber é um serviço incrível!"
    }

    Resposta:
    {
        "vector": [0.23, 0.55, -0.33, ...]
    }
    """
    try:
        text = request.json['text']
        vector = vectorize_text(text)  # Assume que esta função retorna um numpy array.
        return jsonify({'vector': vector.tolist()})  # Converta o numpy array para lista, se necessário.
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    
@vectorize_bp.route('/csv', methods=['POST'])
def vectorize_text_route_csv():
    """
    Esta rota recebe um arquivo CSV contendo texto a ser vetorizado.
    Retorna um arquivo CSV com os vetores.

    Exemplo de request:
    CSV com uma coluna 'text' contendo as frases a serem vetorizadas.
    
    Resposta:
    CSV com a mesma estrutura de linhas e colunas adicionais contendo os vetores.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        file_stream = io.BytesIO(file.read())
        file_stream.seek(0)
    
        data = pd.read_csv(file_stream)
        vectors = vectorize_text(data)

        if vectors is None:
            return jsonify({'message': 'Erro na vetorização'}), 400

        # Cria um DataFrame com os vetores
        vectors_df = pd.DataFrame(vectors)

        # Concatena os vetores ao DataFrame original
        response_data = pd.concat([data, vectors_df], axis=1)
        
        output = io.BytesIO()
        response_data.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='vectorized_data.csv')
    
    except Exception as e:
        print("erro na vetorização: ", e)
        return jsonify({'message': str(e)}), 400
