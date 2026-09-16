from assistant.data_retrieval import get_low_stock_products, get_forecast_summary, get_slow_moving_products
from assistant.llm_client import ask_llm


def extract_product_id(question : str):
    words = question.split()

    for word in words:
        if word.isdigit():
            return int(word)
    return None


def ask_copilot(question : str, db):
    question = question.lower()

    if "low stock" in question or "reorder" in question or "less products" in question:
        data =  get_low_stock_products(db)
        prompt = f"""You are an inventory assistant. Answer only using the data below. Don't make up nnumbers and something by yourself.

                    Data : {data}
                    Question : {question}
                    Answer : """
        return ask_llm(prompt)

    elif "predict" in question or "forecast" in question:
        product_id = extract_product_id(question)
                
        if product_id is None:
            return "Please specify a product ID to get a forecast"
        data =  get_forecast_summary(product_id)
        prompt = f"""You are an inventory assistant. Answer only using the data below. Don't make up nnumbers and something by yourself.
        
                            Data : {data}
                            Question : {question}
                            Answer : """
        return ask_llm(prompt)
    
    elif "slow" in question:
        data =  get_slow_moving_products(db)
        prompt = f"""You are an inventory assistant. Answer only using the data below. Don't make up nnumbers and something by yourself.
        
                            Data : {data}
                            Question : {question}
                            Answer : """
        return ask_llm(prompt)
    
    else:
        return "Sorry, I couldn't understand your question. Try asking about low stock, forecasts, or slow-moving products."
