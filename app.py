from flask import Flask, request, render_template
from QAPredictor import QAPredictor  # Assuming this class exists in your project
from DataProcessor import DataProcessor
app = Flask(__name__)

# Initialize conversation history
conversation_history = []

# Initialize your QAPredictor instance
predictor = QAPredictor()  # Assuming QAPredictor needs to be instantiated

@app.route('/')
def home():
    return render_template('index.html', conversation=conversation_history)
@app.route('/predict', methods=['POST'])
def predict():
    global conversation_history
    try:
        query = request.form.get('query')  # User's question
        user_answer = request.form.get('user_answer')  # User's answer
        retry = False
        second_answer = request.form.get('retry_answer')  # Retry answer

        # Handle question submission
        if query and not user_answer and not second_answer:
            result = predictor.predict(query)
            predicted_answer = result.get('predicted_answer', 'No answer found.')
            feedback = "What could be the right answer? Guess!"
            return render_template(
                'index.html', 
                conversation=conversation_history, 
                feedback=feedback, 
                query=query
            )

        # Handle first answer submission
        if query and user_answer:
            result = predictor.predict(query)
            predicted_answer = result.get('predicted_answer', 'No answer found.')
            if user_answer.lower() == predicted_answer.lower():
                feedback = f"Correct! Your answer: {user_answer} is right."
            else:
                feedback = f"Your answer: {user_answer} is incorrect. Try one mroe time!"
                retry = True
            conversation_history.append({
                "question": query,
                "user_answer": user_answer,
                "predicted_answer": predicted_answer if not retry else "Pending",
                "feedback": feedback
            })
            return render_template(
                'index.html', 
                conversation=conversation_history, 
                feedback=feedback, 
                retry=retry, 
                query=query
            )

        # Handle retry answer submission
        if query and second_answer:
            result = predictor.predict(query)
            predicted_answer = result.get('predicted_answer', 'No answer found.')
            if second_answer.lower() == predicted_answer.lower():
                feedback = f"Your second answer: {second_answer} is correct! The predicted answer is: {predicted_answer}."
            else:
                feedback = f"Sorry! Your answer is still incorrect. The correct answer is: {predicted_answer}. Try next time!"
            conversation_history.append({
                "question": query,
                "user_answer": second_answer,
                "predicted_answer": predicted_answer,
                "feedback": feedback
            })
            return render_template('index.html', conversation=conversation_history, feedback=feedback)

        # If no input is provided, show an error
        return render_template('index.html', conversation=conversation_history, error="You didn't provide an answer. Please try again!")
    except Exception as e:
        return render_template('index.html', conversation=conversation_history, error=str(e))



if __name__ == "__main__":
    app.run(debug=True)
