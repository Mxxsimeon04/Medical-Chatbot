'''
import os, json, random
from flask import Flask, jsonify, request, send_file, send_from_directory
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# ✅ Load model + tokenizer
base_model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
tokenizer.pad_token = tokenizer.eos_token
model = PeftModel.from_pretrained(base_model, "trained_bot/checkpoint-9")

# ✅ Load scenarios from JSONL
with open("qa_data.jsonl", "r", encoding="utf-8") as f:
    scenarios = [json.loads(line.strip()) for line in f if line.strip()]

# ✅ Flask setup
app = Flask(__name__)

@app.route('/')
def home():
    return send_file('web/index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path, cache_timeout=0)

@app.route("/api/scenario", methods=["GET"])
def get_scenario():
    scenario = random.choice(scenarios)
    return jsonify({ "scenario": scenario["scenario"] })  # ✅ not reference_response



@app.route("/api/evaluate", methods=["POST"])
def evaluate_response():
    try:
        data = request.get_json()
        scenario_text = data["scenario"]
        user_response = data["response"]

        # Updated prompt for unique, judgmental evaluation
        prompt = (
            f"You are a medical education evaluator. Evaluate the user's response to a clinical communication scenario.\n\n"
            f"Instructions:\n"
            f"- Provide a realistic score from 1 to 10.\n"
            f"- Give a concise paragraph of constructive feedback about the clinical communication quality.\n"
            f"- Do NOT copy or repeat the scenario or user response.\n"
            f"- Give your answer using this exact format:\n"
            f"Score: 1/10\n"
            f"Feedback: Your response does not address the patient's communication needs.\n\n"
            f"Scenario: {scenario_text}\n"
            f"User Response: {user_response}"
        )

        # Tokenize and generate model output
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        output = model.generate(
            input_ids, 
            max_new_tokens=250, 
            pad_token_id=tokenizer.eos_token_id
        )
        evaluation = tokenizer.decode(output[0], skip_special_tokens=True).strip()

        # Parse Score and Feedback
        score_line = next((line for line in evaluation.splitlines() if "Score:" in line), None)
        feedback_lines = []
        for line in evaluation.splitlines():
            if line.startswith("Feedback:"):
                feedback_lines.append(line)
            elif feedback_lines:
                feedback_lines.append(line)

        if not score_line or not feedback_lines:
            return jsonify({
                "evaluation": "Score: N/A\nFeedback: Unable to parse a valid evaluation. Please retry with a different response."
            })

        final_eval = f"{score_line.strip()}\n{' '.join(line.strip() for line in feedback_lines)}"
        return jsonify({ "evaluation": final_eval })

    except Exception as e:
        return jsonify({ "error": str(e) })



@app.route('/health')
def health():
    return jsonify({ "status": "ok" })

if __name__ == '__main__':
    app.run(debug=True) 
'''

import os, json, random
from flask import Flask, jsonify, request, send_file, send_from_directory
import google.generativeai as genai

# ✅ Directly setting the Gemini API key (not secure for production)
genai.configure(api_key="INSERT-GOOGLE-API-KEY-HERE")


# ✅ Load scenarios from JSONL
with open("qa_data.jsonl", "r", encoding="utf-8") as f:
    scenarios = [json.loads(line.strip()) for line in f if line.strip()]

# ✅ Flask setup
app = Flask(__name__)

@app.route('/')
def home():
    return send_file('web/index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

@app.route("/api/scenario", methods=["GET"])
def get_scenario():
    scenario = random.choice(scenarios)
    return jsonify({ "scenario": scenario["scenario"] })

@app.route("/api/evaluate", methods=["POST"])
def evaluate_response():
    try:
        data = request.get_json()
        scenario_text = data["scenario"]
        user_response = data["response"]

        prompt = (
            f"You are a medical communication evaluator assessing how well a user responds to patients with low English proficiency.\n"
            f"Evaluate whether the user effectively addresses language barriers, uses interpreters or translation appropriately, and shows cultural sensitivity.\n"
            f"Score the response realistically from 1 to 10 and provide clear, constructive feedback.\n\n"
            f"Respond strictly using this format:\n"
            f"Score: x/10\n"
            f"Feedback: <paragraph of thoughtful feedback>\n\n"
            f"Scenario: {scenario_text}\n"
            f"User Response: {user_response}"
        )


        model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ fixed
        response = model.generate_content(prompt)

        return jsonify({ "evaluation": response.text.strip() })

    except Exception as e:
        return jsonify({ "error": str(e) })


@app.route('/health')
def health():
    return jsonify({ "status": "ok" })

if __name__ == '__main__':
    app.run(debug=True)



