from flask import Flask, request, redirect, render_template, url_for, session
import data_manager


app = Flask(__name__)
app.secret_key = '\xc1N}\xd3\xf9\x15\xa3\n*7i\xa6'


@app.route('/')
def route_recent_questions_list():
    questions = data_manager.get_most_recent_questions(5)
    return render_template('index.html', questions=questions)


@app.route('/list')
def route_all_questions_list():
    order_by = request.args.get("order_by")
    if not order_by:
        order_by = "submission_time"
    direction_ = request.args.get("order_direction")
    direction_ = True if direction_ == "asc" else False
    questions = data_manager.get_sorted_questions(order_by, direction_)
    return render_template('index.html', questions=questions, current_dir=direction_)


@app.route('/question/<question_id>/vote-<operation>', methods=['GET', 'POST'])
def route_question_votes(question_id, operation):
    if request.method == 'POST':
        op_change = '+1' if operation == 'up' else '-1'
        data_manager.update_vote_number('question', op_change, question_id)
    return redirect(request.referrer)


@app.route('/answer/<answer_id>/vote-<operation>',  methods=['GET', 'POST'])
def route_answer_votes(answer_id, operation):
    if request.method == 'POST':
        op_change = '+1' if operation == 'up' else '-1'
        data_manager.update_vote_number('answer', op_change, answer_id)
        answer = data_manager.get_record_by_id('answer', answer_id)
        return redirect(url_for('route_question_display', question_id=answer['question_id']))
    return redirect('')


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def route_question_display(question_id):
    tag = data_manager.get_tag_by_question_id(question_id)
    if tag == []:
        current_tag = None
    else:
        tag = tag[0]['tag_id']
        current_tag = data_manager.get_record_by_id("tag", tag)
    template_name = "record-details.html"
    question = data_manager.get_question_with_user_info(question_id)
    if question is None:
        return render_template(template_name, question_id=question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    comments = data_manager.get_comment_by_parent_id('question_id', question_id)
    return render_template(template_name, question=question, answers=answers, comments=comments, tag=current_tag)


@app.route('/answer/<answer_id>')
def route_answer_display(answer_id):
    answer = data_manager.get_answer_with_user_info(answer_id)
    comments = data_manager.get_comment_by_parent_id('answer_id', answer_id)
    return render_template('record-details.html', answer=answer, comments=comments)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):
    edited_question = request.form.to_dict()
    if edited_question:
        data_manager.update_question(question_id, **edited_question)
        return redirect(url_for('route_question_display', question_id=question_id))
    question = data_manager.get_record_by_id("question", question_id)
    return render_template('add-edit.html', data=question, type='question', id=question_id)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_add_answer(question_id):
    if 'name' not in session:
        return render_template('warning.html', message='You need to log in to add an answer')
    if request.method == 'POST':
        new_answer = request.form.to_dict()
        new_answer['vote_number'] = 0
        new_answer['question_id'] = question_id
        user_id_dict = data_manager.get_user_id_by_user_name(session['name'])
        new_answer['user_id'] = user_id_dict['id']
        if new_answer['image'] == '':
            del new_answer['image']
        data_manager.insert_new_record('answer', new_answer)
        return redirect(f'/question/{question_id}')
    return render_template('add-edit.html', parent_id=question_id, parent='question', type='answer')


@app.route('/question/<question_id>/delete', methods=['GET', 'POST'])
def route_delete_question(question_id):
    data_manager.delete_by_id('question', question_id)
    return redirect('/')


@app.route('/answer/<answer_id>/delete', methods=['GET', 'POST'])
def route_delete_answer(answer_id):
    answer = data_manager.get_record_by_id('answer', answer_id)
    question_id = answer['question_id']
    data_manager.delete_by_id('answer', answer_id)
    return redirect(url_for('route_question_display', question_id=question_id))


@app.route('/add-question', methods=['GET', 'POST'])
def route_question_add():
    if 'name' not in session:
        return render_template('warning.html', message='You need to log in to ask a question')
    if request.method == 'POST':
        new_question = request.form.to_dict()
        user_id_dict = data_manager.get_user_id_by_user_name(session['name'])
        new_question['user_id'] = user_id_dict['id']
        new_question['view_number'] = 0
        new_question['vote_number'] = 0
        if new_question['image'] == '':
            del new_question['image']
        data_manager.insert_new_record('question', new_question)
        id_ = data_manager.get_max_id('question')
        id_ = id_['max']
        return redirect('/question/%s' % id_)
    return render_template('add-edit.html', type='question')


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def route_add_comment_to_question(question_id):
    if 'name' not in session:
        return render_template('warning.html', message='You need to log in to add a comment')
    new_comment = request.form.to_dict()
    if new_comment:
        user_id_dict = data_manager.get_user_id_by_user_name(session['name'])
        new_comment['user_id'] = user_id_dict['id']
        data_manager.insert_new_record('comment', new_comment)
        return redirect(url_for('route_question_display', question_id=question_id))
    return render_template('add-edit.html', parent_id=question_id, parent='question', type='comment')


@app.route('/answer/<answer_id>/new_comment', methods=['GET', 'POST'])
def route_add_comment_to_answer(answer_id):
    if 'name' not in session:
        return render_template('warning.html', message='You need to log in to add a comment')
    new_comment = request.form.to_dict()
    if new_comment:
        user_id_dict = data_manager.get_user_id_by_user_name(session['name'])
        new_comment['user_id'] = user_id_dict['id']
        data_manager.insert_new_record('comment', new_comment)
        return redirect(url_for('route_answer_display', answer_id=answer_id))
    return render_template('add-edit.html', parent_id=answer_id, parent='answer', type='comment')


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def route_edit_answer(answer_id):
    question_id = request.form.get('question_id')
    if question_id is not None:
        message = request.form.get('message')
        image = request.form.get('image')
        data_manager.update_answer(message, image, answer_id)
        return redirect(url_for('route_question_display', question_id=question_id))
    answer = data_manager.get_record_by_id('answer', answer_id)
    return render_template('add-edit.html', data=answer, id=answer_id, type='answer')


@app.route('/comments/<comment_id>/edit', methods=['POST', 'GET'])
def route_edit_comment(comment_id):
    message = request.form.get('message')
    if message:
        edited_count = request.form.get('edited_count')
        edited_count = 1 if edited_count == 'None' else int(edited_count) + 1
        new_values = {'edited_count': edited_count, 'message': message}
        data_manager.update_comment_by_primary_id(new_values, comment_id)
        parent_id = request.form.get('question_id')
        if parent_id:
            return redirect(url_for('route_question_display', question_id=parent_id))
        parent_id = request.form.get('answer_id')
        return redirect(url_for('route_answer_display', answer_id=parent_id))
    comment = data_manager.get_record_by_id('comment', comment_id)
    return render_template('add-edit.html', data=comment, id=comment_id, type='comment')


@app.route('/search')
def route_search_results():
    search_phrase = request.args.get('search_phrase')
    if search_phrase == '':
        return redirect('/list')
    else:
        data_found = data_manager.get_search_results_from_database(f'%{search_phrase}%')
        return render_template('search-results.html', data_found=data_found, search_phrase=search_phrase)


@app.route('/comments/<comment_id>/delete', methods=['POST', 'GET'])
def route_delete_comment(comment_id):
    if request.method == 'POST':
        comment = data_manager.get_record_by_id('comment', comment_id)
        data_manager.delete_by_id('comment', comment_id)
        if comment['question_id'] is not None:
            return redirect(f"/question/{comment['question_id']}")
        return redirect(f"/answer/{comment['answer_id']}")
    return render_template('warning.html', message='Action denied')


@app.route('/question/<question_id>/add-edit-tag', methods=['GET', 'POST'])
def route_add_edit_tag(question_id):
    tags = data_manager.get_basic_tags()
    tag_id = data_manager.get_tag_by_question_id(question_id)
    if tag_id == []:
        tag_id = None
    else:
        tag_id = tag_id[0]['tag_id']
        tag_id = data_manager.get_record_by_id('tag', tag_id)
    if request.method == 'POST':
        ntag = request.form.to_dict()
        question_id = ntag['question_id']
        if ntag['define_own'] == '':
            del ntag['define_own']
            ntag['name'] = ntag.pop('select')
        else:
            del ntag['select']
            ntag['name'] = ntag.pop('define_own')
        if ntag['tag_id'] == '':
            data_manager.insert_new_tag(ntag)
        else:
            data_manager.update_tag(ntag)
        return redirect(f'/question/{question_id}')
    return render_template('add-edit-tag.html', question_id=question_id, tags=tags, tag_id=tag_id)


@app.route('/question/<question_id>/<tag>/delete')
def route_delete_tag(question_id, tag):
    data_manager.delete_tags(question_id, tag)
    return redirect(f'/question/{question_id}')


@app.route('/registration', methods=['GET', 'POST'])
def route_register_user():
    if request.method == 'POST':
        user_data = request.form.to_dict()
        success = data_manager.register_user(user_data['name'], user_data['password'])
        if success:
            return redirect(url_for('route_all_questions_list'))
        msg = 'Username already taken'
        return render_template('registration.html', type='registration', warning_message=msg)
    return render_template('registration.html', type='registration')


@app.route('/login', methods=['GET', 'POST'])
def route_login():
    if request.method == 'POST':
        role_id = data_manager.get_role_id_if_user_exists(request.form['name'])
        if role_id:
            password_hash = data_manager.get_password_hash_by_name(request.form['name'])
            valid_user_data = data_manager.verify_password(request.form['password'], password_hash)
            if valid_user_data:
                session['name'] = request.form['name']
                session['role_id'] = role_id
                return redirect(url_for('route_all_questions_list'))
        msg = 'Invalid password or username'
        return render_template('registration.html', type='login', warning_message=msg)
    return render_template('registration.html', type='login')


@app.route('/logout')
def logout():
    session.pop('name', None)
    session.pop('role_id', None)
    return redirect(url_for('route_all_questions_list'))


@app.route('/user/<name>', methods=['GET'])
def route_user_page(name):
    user = data_manager.get_user_data(name)
    user_id = user['user_id']
    reputation = data_manager.get_user_reputation(user_id)
    if reputation is not None:
        if reputation['answer_votes'] is None:
            reputation['answer_votes'] = 0
        if reputation['question_votes'] is None:
            reputation['question_votes'] = 0
    questions = data_manager.get_questions_by_user_id(user_id)
    answers = data_manager.get_answers_by_user_id(user_id)
    comments = data_manager.get_comments_by_user_id(user_id)
    return render_template(
        'user-page.html',
        user=user,
        reputation=reputation,
        questions=questions,
        answers=answers,
        comments=comments)


@app.route('/edit-user/<name>/<what_to_do>', methods=['GET'])
def edit_user(name, what_to_do):
    if 'role_id' not in session or session['role_id'] != 1:
        message = "You don't have the right to access this page"
        return render_template('warning.html', message=message)
    data_manager.edit_user_data(name, what_to_do)
    if session['name'] == name:
        logout()
    return redirect(url_for('route_recent_questions_list'))


@app.route('/all-users', methods=['GET'])
def route_list_all_users():
    data = data_manager.get_all_user_data()
    return render_template('user-page.html', data=data)


@app.route('/all-tags', methods=['GET'])
def route_list_all_tags():
    tags = data_manager.get_all_tags_questions()
    unique_tags = set(tag['tag'] for tag in tags)
    return render_template('user-page.html', tags=tags, unique_tags=unique_tags)


if __name__ == '__main__':
    app.run(debug=True)
