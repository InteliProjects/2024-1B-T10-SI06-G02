import sqlite3
from datetime import datetime, timedelta

class DbContext:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def get_connection(self):
        if not self.conn:
            self.conn = sqlite3.connect('./database/nexusDB.sqlite')
            self.cursor = self.conn.cursor()
        return self.conn, self.cursor

    def query(self, sql):
        conn, cursor = self.get_connection()
        cursor.execute(sql)
        return cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
            
    def addPredictions(self, predictions):
        try:
            for prediction in predictions:
                self.addPrediction(prediction)
            return True
        except Exception as e:
            print("Erro ao adicionar predições no banco de dados: ", e)
            return False
        
    
    def addPrediction(self, prediction):
        try:
            self.conn, self.cursor = self.get_connection()
            comment = prediction["comment"]
            sentiment = prediction["sentiment"]
            
            counts = self.positiveAndNegativeCount()
            total = counts["negative"] + counts["positive"]
            
            previous_count = counts["negative" if sentiment == 0 else "positive"]
            current_count = previous_count + 1
            
            previous_percentage = previous_count / total if total > 0 else 0
            current_percentage = current_count / (total + 1)
            difference = current_percentage - previous_percentage
            
            self.cursor.execute("INSERT INTO Comment(comment, sentiment, previous_percentage, current_percentage, difference) VALUES (?,?,?,?,?)", (comment, sentiment, previous_percentage, current_percentage, difference))
            self.conn.commit()
            
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print("Erro SQLite ao adicionar predição no banco de dados:", e)
        except Exception as e:
            print("Erro ao adicionar predição no banco de dados:", e)

            
    def positiveAndNegativeCount(self, periodInDays=None):
        try:
            if not self.conn:
                self.conn, self.cursor = self.get_connection()
            negative = 0
            positive = 0
            period = None
            if periodInDays == None:
                self.cursor.execute("SELECT COUNT(*) FROM Comment WHERE sentiment = 0")
                negative = self.cursor.fetchall()
                self.cursor.execute("SELECT COUNT(*) FROM Comment WHERE sentiment = 1")
                positive = self.cursor.fetchall()
            else:
                period = datetime.now() - timedelta(days=periodInDays)
                self.cursor.execute("SELECT COUNT(*) FROM Comment WHERE sentiment = 0 AND createdAt >= ?", (period,))
                negative = self.cursor.fetchall()
                self.cursor.execute("SELECT COUNT(*) FROM Comment WHERE sentiment = 1 AND createdAt >= ?", (period,))
                positive = self.cursor.fetchall()
                
            return {"negative": negative[0][0], "positive": positive[0][0]}
        except Exception as e:
            print("Erro ao contar comentários no banco de dados: ", e)
            return None
        
    
    def lastThreePredictions(self):
        if not self.conn:
            self.conn, self.cursor = self.get_connection()
        # Select the last 3 comments by createdAt
        self.cursor.execute("SELECT * FROM Comment ORDER BY createdAt DESC LIMIT 3")
        return self.cursor.fetchall()

