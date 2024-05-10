class Job:
    def __init__(self, company, title, status, application_num, num_openings, work_duration, location, description, responsibilities, skills, pay = None, rating = None, num_rating = None, compatibility = None):
        self.company = company
        self.title = title
        self.status = status
        self.application_num = application_num
        self.num_openings = num_openings
        self.work_duration = work_duration 
        self.location = location
        self.description = description
        self.responsibilities = responsibilities
        self.skills = skills
        self.pay = pay
        self.rating = rating
        # TODO: self.hires_by_work_term
        # TODO: self.hires_by_faculty
        # TODO: self.hires_by_program
        self.num_rating = num_rating
        self.compatibility = compatibility # 0 - 1
        
    # [company, title, status, applicates per position, work duration, location, description, responsibilities, skills, pay, rating, num_rating]
    def to_list(self):
        return [self.company, self.title, self.status, self.application_num / self.num_openings, self.work_duration, self.location,
                self.pay, self.rating, self.num_rating, self.description, self.responsibilities, self.skills]