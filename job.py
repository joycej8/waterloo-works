class Job:
    def __init__(self, company, title, status, application_num, num_openings, work_duration, location, location_arrangement, additional_application, description, responsibilities, skills, pay = None, rating = None, num_rating = None, programs_hired = None, faculty_hired = None, work_term_hired = None):
        self.company = company
        self.title = title
        self.status = status
        self.application_num = application_num
        self.num_openings = num_openings
        self.applicants_per_position = round(application_num / num_openings, 2)
        self.work_duration = work_duration
        self.location = location
        self.location_arrangement = location_arrangement
        self.additional_application = additional_application
        self.description = description
        self.responsibilities = responsibilities
        self.skills = skills
        self.pay = pay
        self.rating = rating
        self.num_rating = num_rating
        self.hires_by_program = programs_hired
        self.hires_by_faculty = faculty_hired
        self.hires_by_work_term = work_term_hired
        self.confidence = 0

    @staticmethod
    def attribute_titles():
        return {
            'confidence': 'Confidence',
            'company': 'Company',
            'title': 'Title',
            'status': 'Status',
            'applicants_per_position': 'Applicants per Position',
            'work_duration': 'Work Duration',
            'location': 'Location',
            'location_arrangement': 'Location Arrangement',
            'pay': 'Pay',
            'rating': 'Rating',
            'num_rating': 'Number of Ratings',
            'hires_by_program': 'Hires by Program',
            'hires_by_faculty': 'Hires by Faculty',
            'hires_by_work_term': 'Hires by Work Term',
            'description': 'Description',
            'responsibilities': 'Responsibilities',
            'skills': 'Skills',
            'additional_application': 'Additional Application'
        }

    @staticmethod
    def get_names():
        return list(Job.attribute_titles().values())
    
    def get_job_attributes(self):
        return [getattr(self, attr) for attr in self.attribute_titles()]