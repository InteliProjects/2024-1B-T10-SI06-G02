from flask import Flask, Blueprint, jsonify, request, send_file
from services.DbContext import DbContext

infos_bp = Blueprint('infos', __name__)


@infos_bp.route("/graph-infos/<int:period_in_days>", methods=['GET'])
def getInfos(period_in_days):
    db = DbContext()
    try:
        # Obtenha os dados conforme o período fornecido
        counts = db.positiveAndNegativeCount(period_in_days)
        # Feche a conexão com o banco de dados
        db.close()
        
        # Retorne os dados como uma resposta JSON
        return jsonify(counts), 200
    except Exception as e:
        # Em caso de erro, retorne uma mensagem de erro
        return jsonify({"error": str(e)}), 500
    
@infos_bp.route("/last_tweets", methods=['GET'])
def getLastTweets():
    db = DbContext()
    try:
        # Obtenha os últimos tweets
        tweets = db.lastThreePredictions()
        # Feche a conexão com o banco de dados
        db.close()
        
        # Retorne os dados como uma resposta JSON
        #{"last_tweets": tweets}
        return jsonify({"last_tweets": tweets}), 200
    except Exception as e:
        # Em caso de erro, retorne uma mensagem de erro
        return jsonify({"error": str(e)}), 500
    
@infos_bp.route("/alert", methods=['GET'])
def alert():
    db = DbContext()
    try:
        counts1day = db.positiveAndNegativeCount(0.01)
        counts2days = db.positiveAndNegativeCount(1)
        
        negatives1day = counts1day["negative"]
        negatives2days = counts2days["negative"] - negatives1day
        
        print("negatives1day: ", negatives1day)
        print("negatives2days: ", negatives2days)
        
        if negatives2days == 0:
            return jsonify({"alert": False}), 200
        
        aumento = negatives1day/negatives2days
        
        print("aumento: ", aumento)
        if aumento > 1.2:
            return jsonify({"alert": True, "increase":aumento-1}), 200
        else:
            return jsonify({"alert": False}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
           
    