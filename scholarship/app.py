from flask import Flask, request
import csv

app = Flask(__name__)

SCHOLARSHIP_FILE = "scholarships.csv"

def load_scholarships():
    scholarships = []
    with open(SCHOLARSHIP_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # normalize and convert types
            row["eligible_courses"] = [c.strip().lower() for c in row["eligible_courses"].split(";")]
            row["min_percentage"] = float(row["min_percentage"])
            row["max_income"] = float(row["max_income"])
            row["region"] = row["region"].strip().lower()
            scholarships.append(row)
    return scholarships

@app.route("/")
def form():
    return """
    <h1>Scholarship Finder</h1>
    <form method="post" action="/find">
      Course: <input name="course" required><br><br>
      Percentage: <input type="number" name="percent" step="0.01" required><br><br>
      Annual Family Income: <input type="number" name="income" required><br><br>
      Region: <input name="region" required><br><br>
      <button type="submit">Search</button>
    </form>
    """

@app.route("/find", methods=["POST"])
def find():
    course = request.form.get("course", "").strip().lower()
    percent = float(request.form.get("percent", "0"))
    income = float(request.form.get("income", "0"))
    region = request.form.get("region", "").strip().lower()

    matches = []
    for s in load_scholarships():
        course_ok = course in s["eligible_courses"]
        percent_ok = percent >= s["min_percentage"]
        income_ok = income <= s["max_income"]
        region_ok = (s["region"] == "all") or (s["region"] == region)
        if course_ok and percent_ok and income_ok and region_ok:
            matches.append(s)

    if not matches:
        return "<h3>No scholarships found matching your profile.</h3><p><a href='/'>Try again</a></p>"

    output = "<h2>Eligible Scholarships:</h2>"
    for m in matches:
        output += f"""
        <div style="border:1px solid #444; padding:10px; margin:10px;">
          <strong>{m['name']}</strong><br>
          Description: {m['description']}<br>
          Eligible Courses: {', '.join(m['eligible_courses'])}<br>
          Min %: {m['min_percentage']} | Max Income: ₹{int(m['max_income'])}<br>
          Region: {m['region'].title()}<br>
          Deadline: {m.get('deadline', 'N/A')}<br>
        </div>
        """
    output += "<p><a href='/'>Search again</a></p>"
    return output

if __name__ == "__main__":
    app.run(debug=True)
