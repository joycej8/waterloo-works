class Job:
    def __init__(self, company, title, status, application_num, num_openings, work_duration, location, location_arrangement, description, responsibilities, skills, pay = None, rating = None, num_rating = None, programs_hired = None, faculty_hired = None, work_term_hired = None):
        self.company = company
        self.title = title
        self.status = status
        self.application_num = application_num
        self.num_openings = num_openings
        self.work_duration = work_duration 
        self.location = location
        self.location_arrangement = location_arrangement
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

    # [company, title, status, applicates per position, work duration, location, description, responsibilities, skills, pay, rating, num_rating]
    def to_list(self):
        return [self.confidence, self.company, self.title, self.status, round(self.application_num / self.num_openings, 2), self.work_duration, self.location, self.location_arrangement,
                self.pay, self.rating, self.num_rating, self.hires_by_program, self.hires_by_faculty, self.hires_by_work_term, self.description, self.responsibilities, self.skills]
