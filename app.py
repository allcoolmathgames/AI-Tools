from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)

# Dummy data store (real project mein database use hoga)
courses_data = [] # For Page 1

# --- Helper function to calculate GPA ---
def calculate_gpa_from_courses():
    total_grade_points = 0
    total_credits = 0
    grade_map = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0
    }

    for course in courses_data:
        if 'grade' in course and course['grade'] in grade_map and \
           'credits' in course and isinstance(course['credits'], (int, float)):
            grade_points = grade_map[course['grade']] * course['credits']
            total_grade_points += grade_points
            total_credits += course['credits']

    if total_credits == 0:
        return 0.0
    return round(total_grade_points / total_credits, 2)

# --- Routes for pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prior-semester-gpa')
def prior_semester_gpa():
    return render_template('prior-semester-final-gpa.html')

@app.route('/highschool-gpa')
def highschool_gpa():
    return render_template('highschool.html')

@app.route('/gpa-calculator')
def gpa_calculator():
    return render_template('gpa-calculator.html')

@app.route('/gpa-planning')
def gpa_planning():
    return render_template('gpa-planning-calculator.html')

# --- Blog Routes ---
@app.route('/blogs')
def blog_index():
    return render_template('blogs/blog_index.html')

@app.route('/blogs/<slug>')
def blog_post(slug):
    blog_templates = {
        'how-to-improve-your-gpa-effectively': 'blogs/gpa_blog.html',
        'understanding-different-grading-scales': 'blogs/final_gpa_blog.html',
        'achieving-your-target-gpa-guide': 'blogs/target_gpa_blog.html'
    }
    
    template_to_render = blog_templates.get(slug)
    
    if template_to_render:
        return render_template(template_to_render, slug=slug)
    else:
        return "Blog Post Not Found", 404

# --- Other Static Pages (from 'pages' folder) ---
@app.route('/privacy')
def privacy_policy():
    return render_template('pages/privacy.html')

@app.route('/terms_conditions')
def terms_conditions():
    return render_template('pages/terms_conditions.html')

@app.route('/aboutus')
def about_us():
    return render_template('pages/Aboutus.html')

@app.route('/contact')
def contact():
    return render_template('pages/Contact.html')

# --- API Endpoints for Page 1 (Main GPA Calculator) ---
@app.route('/get_courses', methods=['GET'])
def get_courses():
    return jsonify({'status': 'success', 'courses': courses_data, 'currentGpa': calculate_gpa_from_courses()})

@app.route('/add_course', methods=['POST'])
def add_course():
    data = request.json
    course_name = data.get('courseName')
    credits = data.get('credits')
    grade = data.get('grade')
    
    if not course_name or not grade:
        return jsonify({'status': 'error', 'message': 'Course Name and Grade are required.'}), 400
    try:
        credits = float(credits)
        if credits <= 0:
            return jsonify({'status': 'error', 'message': 'Credits must be a positive number.'}), 400
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid Credits value.'}), 400
    
    grade_map_keys = {'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'}
    if grade not in grade_map_keys:
        return jsonify({'status': 'error', 'message': 'Invalid Grade. Allowed grades are A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F.'}), 400

    courses_data.append({'name': course_name, 'credits': credits, 'grade': grade})
    
    return jsonify({'status': 'success', 'courses': courses_data, 'currentGpa': calculate_gpa_from_courses()})

@app.route('/update_course', methods=['POST'])
def update_course():
    data = request.json
    index = data.get('index')
    new_credits = data.get('credits')
    new_grade = data.get('grade')
    
    if not (0 <= index < len(courses_data)):
        return jsonify({'status': 'error', 'message': 'Course not found at specified index.'}), 404
    
    try:
        if new_credits is not None:
            new_credits = float(new_credits)
            if new_credits <= 0:
                return jsonify({'status': 'error', 'message': 'Credits must be a positive number.'}), 400
            courses_data[index]['credits'] = new_credits
        
        if new_grade:
            grade_map_keys = {'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'}
            if new_grade not in grade_map_keys:
                return jsonify({'status': 'error', 'message': 'Invalid Grade. Allowed grades are A+, A, A-, B+, B, B-,C+, C, C-, D+, D, D-, F'}), 400
            courses_data[index]['grade'] = new_grade
            
        return jsonify({'status': 'success', 'courses': courses_data, 'currentGpa': calculate_gpa_from_courses()})
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid data for update.'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/delete_course', methods=['POST'])
def delete_course():
    data = request.json
    index = data.get('index')
    
    if not (0 <= index < len(courses_data)):
        return jsonify({'status': 'error', 'message': 'Course not found at specified index.'}), 404
    
    del courses_data[index]
    
    return jsonify({'status': 'success', 'courses': courses_data, 'currentGpa': calculate_gpa_from_courses()})

@app.route('/reset_courses', methods=['POST'])
def reset_courses():
    global courses_data
    courses_data = []
    return jsonify({'status': 'success', 'message': 'All courses cleared.', 'currentGpa': 0.0})


# --- API Endpoints for Page 2 (Prior Semester / Final GPA Calculator) ---
@app.route('/calculate_combined_gpa', methods=['POST'])
def calculate_combined_gpa():
    data = request.json
    try:
        old_total_credits = float(data.get('oldTotalCredits'))
        old_gpa = float(data.get('oldGpa'))
        new_semester_credits = float(data.get('newSemesterCredits'))
        new_semester_gpa = float(data.get('newSemesterGpa'))

        if old_total_credits < 0 or old_gpa < 0 or new_semester_credits < 0 or new_semester_gpa < 0:
            return jsonify({'status': 'error', 'message': 'All credit and GPA values must be non-negative.'}), 400
        if old_gpa > 4.0 or new_semester_gpa > 4.0:
            return jsonify({'status': 'error', 'message': 'GPA cannot exceed 4.0.'}), 400

        old_grade_points = old_total_credits * old_gpa
        new_grade_points = new_semester_credits * new_semester_gpa
        
        combined_total_credits = old_total_credits + new_semester_credits
        combined_total_grade_points = old_grade_points + new_grade_points
        
        combined_gpa = round(combined_total_grade_points / combined_total_credits, 2) if combined_total_credits > 0 else 0.0
        
        return jsonify({'status': 'success', 'combinedGpa': combined_gpa})
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid input: Please provide valid numbers.'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/calculate_final_cumulative_gpa', methods=['POST'])
def calculate_final_cumulative_gpa():
    data = request.json
    try:
        total_credits = float(data.get('totalCredits'))
        gpa = float(data.get('gpa'))

        if total_credits < 0 or gpa < 0:
            return jsonify({'status': 'error', 'message': 'Credits and GPA must be non-negative.'}), 400
        if gpa > 4.0:
            return jsonify({'status': 'error', 'message': 'GPA cannot exceed 4.0.'}), 400

        final_gpa = round(gpa, 2)

        return jsonify({'status': 'success', 'finalGpa': final_gpa})
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid input: Please provide valid numbers.'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500

# --- API Endpoints for Page 3 (GPA Planning) ---
@app.route('/calculate_required_gpa', methods=['POST'])
def calculate_required_gpa():
    data = request.json
    try:
        goal_gpa = float(data.get('goalGpa'))
        current_gpa = float(data.get('currentGpa'))
        current_total_credits = float(data.get('currentTotalCredits'))
        next_semester_credits = float(data.get('nextSemesterCredits'))
        
        if goal_gpa < 0 or current_gpa < 0 or current_total_credits < 0 or next_semester_credits <= 0:
            return jsonify({'status': 'error', 'message': 'All credit and GPA values must be non-negative, and Next Semester Credits must be greater than zero.'}), 400
        if goal_gpa > 4.0 or current_gpa > 4.0:
            return jsonify({'status': 'error', 'message': 'GPA cannot exceed 4.0.'}), 400

        desired_total_grade_points = (current_total_credits + next_semester_credits) * goal_gpa
        current_grade_points = current_total_credits * current_gpa
        
        required_grade_points_for_next_semester = desired_total_grade_points - current_grade_points
        
        required_gpa = round(required_grade_points_for_next_semester / next_semester_credits, 2)
        
        message = ""
        if required_gpa > 4.0:
            message = 'The required GPA is very high. It might be impossible to achieve your goal with the given credits.'
        elif required_gpa < 0.0:
            message = 'The required GPA is negative, meaning you can achieve your goal even with a lower GPA in the next semester.'
        
        return jsonify({'status': 'success', 'requiredGpa': required_gpa, 'message': message})
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid input: Please provide valid numbers.'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)