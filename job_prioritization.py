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

    def get_category(self, category):
        try:
            return self.config_data.get(category)
        except:
            logging.error(f"yaml contains no value {category}")

    def get_item(self, category, item):
        try:
            return self.config_data.get(category).get(item)
        except:
            logging.error(f"yaml contains no value {item} at {category}")
    
config = Config('user_preferences.yaml')

def sort_shortlisted_by_confidence(shortlisted):
    try:
        for job in shortlisted:
            user_details = config.get_category("user_details")

            employment_duration_score = is_preference_matched(user_details["employment_duration_months"], job.work_duration)
            hourly_rate_score = get_confidence_value_exponential(user_details["hourly_rate"], job.pay)
            study_program_score = get_program_value(user_details["study_program"], job.hires_by_program)
            academic_faculty_score = get_dict_value(user_details["academic_faculty"], job.hires_by_faculty)
            work_term_score = get_dict_value(user_details["current_work_term"], job.hires_by_work_term)
            rating_score = get_rating_value(job.rating)

            scores = [employment_duration_score, hourly_rate_score, study_program_score, academic_faculty_score, work_term_score, rating_score]
            priority_weights = config.get_category("priority_weights").values()
            
            calculate_confidence(job, scores, priority_weights)

        sorted_shortlist = sorted(shortlisted, key=lambda job: job.confidence, reverse=True)
        return sorted_shortlist

    except Exception as e:
            logging.error(f"sort_shortlisted_by_confidence failed {e}")

def calculate_confidence(job, scores, weights):
    try:
        # Normalize weights if they don't sum up to 1
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        weighted_average = sum(score * weight for score, weight in zip(scores, normalized_weights))
        overall_confidence = round(weighted_average * 100, 2)

        job.confidence = overall_confidence
    except Exception as e:
        logging.error(f"calculate_confidence failed {e}")

# faculty and work term
def get_dict_value(key, dict_values):
    if dict_values:
        if key in dict_values:
            return dict_values[key]
        else:
            return 0
    else:
        return 0.1

# for rating
def get_rating_value(rating):
    if rating:
        return rating / 10
    else:
        return 0.5

# for program
def get_program_value(program, programs):
    if programs:
        if program in programs:
            total = sum(programs.values())
            program_count = programs[program]
            return program_count / total
        else:
            return 0
    else:
        return 0.05

# for employment_duration_months
def is_preference_matched(value, user_preference_value):
    user_preference_value = int(user_preference_value[0])
    if value == user_preference_value:
        return 1
    else:
        return 0
    
# for pay
def get_confidence_value_exponential(point_estimate, x_value, max_value=70):
    if x_value:
        x_value = max_value - x_value
        scale = max(1, max_value - point_estimate)
        y_value_at_x = expon.pdf(x_value, scale=scale)
    else: # Return the PDF value at the mean
        scale = max(1, max_value - point_estimate)
        y_value_at_x = expon.pdf(scale, scale=scale)

    x_positive = np.linspace(18, max_value, 1000)  # Generate x values
    pdf_values = expon.pdf(x_positive, scale=scale)  # Calculate the PDF for these x values
    max_pdf_value = np.max(pdf_values)

    normalized_y_value_at_x = y_value_at_x / max_pdf_value
    return normalized_y_value_at_x

# TODO: for status
def get_status_value(status):
    if status == "Open for Applications":
        return 1
    else:
        return 0

# TODO: for applicants per position
def get_confidence_value_gaussian(point_estimator, x_value, std_dev=0.1):
    gaussian_dist = norm(loc=point_estimator, scale=std_dev)
    y_value_at_x = gaussian_dist.pdf(x_value)

    x_range = np.linspace(-1, 2, 1000)
    pdf_values = gaussian_dist.pdf(x_range)

    # Find the normalized y_value at the specific x_value
    normalized_y_value_at_x = y_value_at_x / pdf_values.max()

    return normalized_y_value_at_x
    
# TODO: for location
def get_location_value(location):
    # 0 for remote work?
    pass

# TODO: for desscription, responsibility, skills