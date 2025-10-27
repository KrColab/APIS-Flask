from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS

import json
import numpy as np
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Povolenie CORS – fajn na vývoj, v produkcii radšej obmedziť domény.

# cesta k súboru so študentmi.
DATA_PATH = Path(__file__).parent / "students.json"


def _load_students_or_error():
    """Load students.json and return list or None on error."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


@app.get("/Students")
def students():
    """Vracia obsah súboru students.json, podporuje jednoduché filtre cez query params.

    Supported query params: City, Town, Gender, Name, id/Id, minYear, maxYear
    """
    data = _load_students_or_error()
    if data is None:
        return jsonify({"error": "students.json not found or invalid"}), 500

    # read filters
    city = request.args.get("City") or request.args.get("Town")
    gender = request.args.get("Gender") or request.args.get("gender")
    name_q = request.args.get("Name") or request.args.get("name")
    id_q = request.args.get("id") or request.args.get("Id")
    min_year_q = request.args.get("minYear") or request.args.get("minyear")
    max_year_q = request.args.get("maxYear") or request.args.get("maxyear")

    student_id = None
    if id_q:
        try:
            student_id = int(id_q)
        except ValueError:
            return jsonify({"error": "id must be an integer"}), 400

    min_year = None
    if min_year_q:
        try:
            min_year = int(min_year_q)
        except ValueError:
            return jsonify({"error": "minYear must be an integer"}), 400

    max_year = None
    if max_year_q:
        try:
            max_year = int(max_year_q)
        except ValueError:
            return jsonify({"error": "maxYear must be an integer"}), 400

    # apply filters
    out = []
    for s in data:
        if student_id is not None and s.get("Id") != student_id:
            continue
        if city and str(s.get("City", "")).lower() != city.lower():
            continue
        if gender and str(s.get("Gender", "")).lower() != gender.lower():
            continue
        if name_q and name_q.lower() not in str(s.get("Name", "")).lower():
            continue
        if min_year is not None:
            by = s.get("BirthYear")
            if not (isinstance(by, int) and by >= min_year):
                continue
        if max_year is not None:
            by = s.get("BirthYear")
            if not (isinstance(by, int) and by <= max_year):
                continue
        out.append(s)

    return jsonify(out), 200


@app.get('/ui')
def ui():
    """Serve the simple filter UI (templates/filter.html)."""
    return render_template('filter.html')


@app.get("/")
def index():
    """Redirect root to the UI page."""
    return redirect(url_for('ui'))


@app.get("/Predict")
def predict():
    """
    Lineárna extrapolácia skóre pre 6. test zo zadaných 5 skóre.
    Očakávaný formát: ?Scores=10 20 30 40 50
    Výstup je orezaný na <0, 100>.
    """
    scores_raw = request.args.get("Scores", "").strip()
    if not scores_raw:
        return jsonify({"error": "Missing Scores. Example: ?Scores=10 20 30 40 50"}), 400

    # Rozparsuj a over čísla
    try:
        y = [float(i) for i in scores_raw.split()]
    except ValueError:
        return jsonify({"error": "Scores must be numbers separated by spaces"}), 400

    if len(y) != 5:
        return jsonify({"error": "Provide exactly 5 scores"}), 400

    # x sú indexy testov 1..5, y sú skóre
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    y = np.array(y, dtype=float)

    # np.polyfit vráti koeficienty lineárnej regresie (m*slope, b*intercept)
    m, b = np.polyfit(x, y, 1)

    # Predikcia pre „6. test“ (extrapolácia)
    pred = m * 6 + b

    # Orezanie na rozsah 0..100
    pred = max(0.0, min(100.0, float(pred)))

    # Konzistentný JSON výstup + zaokrúhlenie
    return jsonify({"prediction": round(pred, 2)}), 200


@app.patch("/Students")
def patch_students():
    """Update students matching query parameters. Body should be JSON with fields to set.
    Example: PATCH /Students?City=Kosice with JSON {"Gender": "Female"}
    """
    updates = request.get_json()
    if not updates or not isinstance(updates, dict):
        return jsonify({"error": "Missing JSON body with fields to update"}), 400

    students = _load_students_or_error()
    if students is None:
        return jsonify({"error": "students.json not found or invalid"}), 500

    city = request.args.get("City") or request.args.get("Town")
    name_q = request.args.get("Name")
    id_q = request.args.get("id") or request.args.get("Id")
    min_year_q = request.args.get("minYear")
    max_year_q = request.args.get("maxYear")

    student_id = None
    if id_q:
        try:
            student_id = int(id_q)
        except ValueError:
            return jsonify({"error": "id must be an integer"}), 400

    min_year = None
    if min_year_q:
        try:
            min_year = int(min_year_q)
        except ValueError:
            return jsonify({"error": "minYear must be an integer"}), 400

    max_year = None
    if max_year_q:
        try:
            max_year = int(max_year_q)
        except ValueError:
            return jsonify({"error": "maxYear must be an integer"}), 400

    updated = 0
    for s in students:
        if student_id is not None and s.get("Id") != student_id:
            continue
        if city and str(s.get("City", "")).lower() != city.lower():
            continue
        if name_q and name_q.lower() not in str(s.get("Name", "")).lower():
            continue
        if min_year is not None and not (isinstance(s.get("BirthYear"), int) and s.get("BirthYear") >= min_year):
            continue
        if max_year is not None and not (isinstance(s.get("BirthYear"), int) and s.get("BirthYear") <= max_year):
            continue

        for k, v in updates.items():
            s[k] = v
        updated += 1

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(students, f, ensure_ascii=False, indent=2)

    return jsonify({"updated": updated}), 200


if __name__ == "__main__":
    # debug=True je užitočné pri vývoji (autoreload, tracebacky)
    # host must be an address only — remove stray '/ui' that caused routing issues.
    app.run(debug=True, host="127.0.0.1", port=5001)
