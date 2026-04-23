from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def init_state():
    return {
        "pieces": [
            ["♜","♞","♝","♛","♚","♝","♞","♜"],
            ["♟","♟","♟","♟","♟","♟","♟","♟"],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["♙","♙","♙","♙","♙","♙","♙","♙"],
            ["♖","♘","♗","♕","♔","♗","♘","♖"],
        ],
        "turn": "white",
        "enPassant": None,
        "castling": {
            "whiteKing": True,
            "whiteQueen": True,
            "blackKing": True,
            "blackQueen": True
        }
    }

game_state = init_state()

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(game_state)

@app.route("/move", methods=["POST"])
def move():
    data = request.json
    fr, fc = data["from"]
    tr, tc = data["to"]
    piece = game_state["pieces"][fr][fc]

    # 앙파상 캡처
    if piece in ["♙","♟"] and fc != tc and game_state["pieces"][tr][tc] == "":
        game_state["pieces"][fr][tc] = ""

    # 캐슬링 룩 이동
    if piece == "♔" and fr == 7 and fc == 4:
        if tc == 6:
            game_state["pieces"][7][5] = game_state["pieces"][7][7]
            game_state["pieces"][7][7] = ""
        if tc == 2:
            game_state["pieces"][7][3] = game_state["pieces"][7][0]
            game_state["pieces"][7][0] = ""
        game_state["castling"]["whiteKing"] = False
        game_state["castling"]["whiteQueen"] = False
    if piece == "♚" and fr == 0 and fc == 4:
        if tc == 6:
            game_state["pieces"][0][5] = game_state["pieces"][0][7]
            game_state["pieces"][0][7] = ""
        if tc == 2:
            game_state["pieces"][0][3] = game_state["pieces"][0][0]
            game_state["pieces"][0][0] = ""
        game_state["castling"]["blackKing"] = False
        game_state["castling"]["blackQueen"] = False

    # 캐슬링 권리 제거
    if piece == "♖":
        if fc == 7: game_state["castling"]["whiteKing"] = False
        if fc == 0: game_state["castling"]["whiteQueen"] = False
    if piece == "♜":
        if fc == 7: game_state["castling"]["blackKing"] = False
        if fc == 0: game_state["castling"]["blackQueen"] = False

    # 이동
    game_state["pieces"][tr][tc] = piece
    game_state["pieces"][fr][fc] = ""

    # 폰 프로모션 (있을 때만 처리, 없어도 계속 진행)
    promo = data.get("promotion", None)
    if promo:
        promo_map = {
            "Q": ("♕","♛"), "R": ("♖","♜"),
            "B": ("♗","♝"), "N": ("♘","♞")
        }
        if piece == "♙" and tr == 0:
            game_state["pieces"][tr][tc] = promo_map.get(promo, ("♕","♛"))[0]
        if piece == "♟" and tr == 7:
            game_state["pieces"][tr][tc] = promo_map.get(promo, ("♕","♛"))[1]

    # 앙파상 설정
    if piece == "♙" and fr - tr == 2:
        game_state["enPassant"] = [fr-1, fc]
    elif piece == "♟" and tr - fr == 2:
        game_state["enPassant"] = [fr+1, fc]
    else:
        game_state["enPassant"] = None

    # 턴 교체
    game_state["turn"] = "black" if game_state["turn"] == "white" else "white"

    return jsonify({"ok": True})

@app.route("/restart", methods=["POST"])
def restart():
    global game_state
    game_state = init_state()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)