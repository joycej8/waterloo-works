import numpy as np
import yaml
import logging
from scipy.stats import norm
from scipy.stats import expon
import matplotlib.pyplot as plt

logging.getLogger().setLevel(logging.INFO)

class Config:
    def __init__(self, filepath):
        self.config_data = self.load_config(filepath)
    
    def load_config(self, filepath):
        try:
            with open(filepath, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logging.error("Configuration file not found.")
            return {}
        except yaml.YAMLError as exc:
            logging.error(f"Error parsing YAML file: {exc}")
            return {}

    def get_preference(self, key, data):
        try:
            return self.config_data.get(key).get(data, 0)
        except:
            logging.error(f"yaml contains no value {key}")
    
config = Config('user_preferences.yaml')

def get_rating_value(rating):
    return rating / 10

def get_work_duration_value(duration):
    months = duration[0]
    if months == 4:
        return config.get_preference("work_duration", 4)
    elif months == 8:
        return config.get_preference("work_duration", 8)
    else:
        return config.get_preference("work_duration", 12)

# Using a exponential distribution, predict y value given x
def get_confidence_value_exponential(point_estimate, x_value, max_value=70):
    x_value = max_value - x_value

    scale = max(1, max_value - point_estimate)  # Determine the scale based on the point_estimate
    
    x_positive = np.linspace(0, max_value, 1000)  # Generate x values
    pdf_values = expon.pdf(x_positive, scale=scale)  # Calculate the PDF for these x values
    max_pdf_value = np.max(pdf_values)

    # Calculate y_value_at_x using the same scale and then normalize it using the max of the normalized PDF
    y_value_at_x = expon.pdf(x_value, scale=scale)
    normalized_y_value_at_x = y_value_at_x / max_pdf_value  # Use max of original pdf_values to align with pdf_normalized

    return normalized_y_value_at_x

# Using a gaussian distribution, predict y value given x
def get_confidence_value_gaussian(point_estimator, x_value, std_dev=0.1):
    gaussian_dist = norm(loc=point_estimator, scale=std_dev)
    y_value_at_x = gaussian_dist.pdf(x_value)

    x_range = np.linspace(-1, 2, 1000)
    pdf_values = gaussian_dist.pdf(x_range)

    # Find the normalized y_value at the specific x_value
    normalized_y_value_at_x = y_value_at_x / pdf_values.max()

    return normalized_y_value_at_x

def get_status_value(status):
    if status == "Open for Applications":
        return 1
    else:
        return 0



