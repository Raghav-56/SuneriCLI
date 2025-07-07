import google.generativeai as genai
import yaml
import os

models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


def get_gemini_model(model_name=models[0]):
    model_name = f"models/{model_name}"
    config_path = os.path.expanduser("config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    genai.configure(api_key=config["gemini_api_key"])
    return genai.GenerativeModel(model_name)


def gemini_generate_content(prompt, model_names=models):
    last_exception = None
    for model_name in model_names:
        try:
            model = get_gemini_model(model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            last_exception = e
            continue
    raise RuntimeError(f"All Gemini models failed. Last error: {last_exception}")
