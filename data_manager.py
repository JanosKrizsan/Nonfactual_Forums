import connection
from datetime import datetime
from psycopg2 import sql
import bcrypt


@connection.connection_handler
def get_max_id(cursor, table):
    cursor.execute(sql.SQL("""
                   SELECT MAX(id) FROM {table};
                   """).format(table=sql.Identifier(table)))
    id_ = cursor.fetchone()
    return id_


@connection.connection_handler
def update_vote_number(cursor, table, operation, id_):
    if operation not in '+1-1':
        raise ValueError(f'{operation} should be +1 or -1.')
    cursor.execute((
        sql.SQL('UPDATE {} SET vote_number = vote_number ' + operation + ' WHERE id=%(id_)s').
        format(sql.Identifier(table))), {'id_': id_})


@connection.connection_handler
def insert_new_record(cursor, table, record):
    record['submission_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    values = ""
    for value in record.values():
        if type(value) is str:
            value = value.replace("'", "''")
        values += (f"'{value}'" if type(value) is str else f"{value}") + ', '
    values = values[:-2] + ')'
    keys = str(tuple(record.keys())).replace("'","")
    cursor.execute(sql.SQL('INSERT INTO {table} ' + keys + ' VALUES (' + values).
                   format(table=sql.Identifier(table)))


@connection.connection_handler
def get_record_by_id(cursor, table, _id):
    cursor.execute(sql.SQL('SELECT * FROM {table} WHERE id=%(_id)s').
                   format(table=sql.Identifier(table)), {'_id': _id})
    record = cursor.fetchone()
    return record


@connection.connection_handler
def get_question_with_user_info(cursor, question_id):
    cursor.execute("""
                   SELECT question.id, user_account.name AS posted_by,
                   question.submission_time, question.view_number, question.vote_number,
                   question.title, question.message, question.image
                   FROM question
                   JOIN user_account ON question.user_id = user_account.id
                   WHERE question.id = %(question_id)s
                   """,
                   {'question_id': question_id})
    record = cursor.fetchone()
    return record


@connection.connection_handler
def get_answer_with_user_info(cursor, answer_id):
    cursor.execute("""
                   SELECT answer.id, user_account.name AS posted_by,
                   answer.submission_time, answer.vote_number, answer.question_id,
                   answer.message, answer.image
                   FROM answer
                   JOIN user_account ON answer.user_id = user_account.id
                   WHERE answer.id = %(answer_id)s
                   """,
                   {'answer_id': answer_id})
    record = cursor.fetchone()
    return record


@connection.connection_handler
def get_comment_by_parent_id(cursor, parent_type, parent_id):
    cursor.execute(sql.SQL("""
                           SELECT comment.id, user_account.name AS posted_by,
                           comment.question_id, comment.answer_id,
                           comment.message, comment.submission_time, comment.edited_count
                           FROM comment
                           JOIN user_account ON comment.user_id = user_account.id
                           WHERE {parent_type} = %(parent_id)s
                           """).format(parent_type=sql.Identifier(parent_type)),
                   {'parent_id': parent_id})
    records = cursor.fetchall()
    return records


@connection.connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute("""
                   SELECT answer.id, user_account.name AS posted_by,
                   answer.submission_time, answer.vote_number, answer.question_id,
                   answer.message, answer.image
                   FROM answer
                   JOIN user_account ON answer.user_id = user_account.id
                   WHERE question_id=%(question_id)s
                   ORDER BY vote_number DESC
                   """,
                   {'question_id': question_id})
    records = cursor.fetchall()
    return records


@connection.connection_handler
def update_comment_by_primary_id(cursor, data, id):
    count, msg = data['edited_count'], data['message']
    cursor.execute("""
                   UPDATE comment
                   SET edited_count= %(count)s, message= %(msg)s
                   WHERE id=%(id)s
                   """,
                   {'count': count, 'msg': msg, 'id': id})


@connection.connection_handler
def update_answer(cursor, message, image, id):
    if image == '':
        cursor.execute("""
                       UPDATE answer SET message= %(message)s
                       WHERE id=%(id)s
                       """,
                       {"message": message, "id": id})
    else:
        cursor.execute("""
                       UPDATE answer SET message= %(message)s, image= %(image)s
                       WHERE id=%(id)s
                       """,
                       {"message": message, "image": image, "id": id})


@connection.connection_handler
def update_question(cursor, id_, message, image, title):
    if image == '':
        cursor.execute("""
                       UPDATE question SET title= %(title)s, message= %(message)s
                       WHERE id=%(id_)s;
                       """,
                       {"title": title, "message": message, "id_": id_})
    else:
        cursor.execute("""
                       UPDATE question SET title= %(title)s, message= %(message)s, image= %(image)s
                       WHERE id=%(id_)s;
                       """,
                       {"title": title, "message": message, "image": image, "id_": id_})


@connection.connection_handler
def get_sorted_questions(cursor, column_to_order_by, asc=True):
    order_direction = 'ASC' if asc is True else 'DESC'
    command = f"""SELECT question.id, submission_time, user_account.name
                  AS posted_by, view_number, vote_number, title, message, image
                  FROM question FULL JOIN user_account ON user_id = user_account.id
                  WHERE submission_time IS NOT NULL
                  ORDER BY {column_to_order_by} {order_direction}
                  """
    cursor.execute(command)
    ordered_table = cursor.fetchall()
    return ordered_table


@connection.connection_handler
def get_most_recent_questions(cursor, amount):
    cursor.execute("""
                   SELECT question.id, question.submission_time,
                   user_account.name AS posted_by, question.view_number, question.vote_number,
                   question.title, question.message, question.image
                   FROM question JOIN user_account ON question.user_id = user_account.id
                   ORDER BY question.submission_time DESC LIMIT %(amount)s
                   """,
                   {'amount': amount})
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_search_results_from_database(cursor, search_phrase):
    cursor.execute("""
                   SELECT DISTINCT ON (title) title, question.message FROM question
                   LEFT JOIN answer ON question.id = answer.question_id
                   WHERE title ILIKE %(search_phrase)s OR question.message
                   ILIKE %(search_phrase)s OR answer.message ILIKE %(search_phrase)s;
                   """,
                   {'search_phrase': search_phrase})
    search_results = cursor.fetchall()
    return search_results


@connection.connection_handler
def delete_by_id(cursor, table, id_, parent_='id'):
    cursor.execute((sql.SQL("""
                            DELETE FROM {table}
                            WHERE {parent_} = %(id_)s
                            """).
                    format(table=sql.Identifier(table), parent_=sql.Identifier(parent_))),
                   {'id_': id_})


@connection.connection_handler
def get_answer_ids(cursor, question_id):
    cursor.execute("""
                   SELECT id FROM answer
                   WHERE question_id=%(question_id)s
                   """,
                   {'question_id': question_id})
    answer_ids = cursor.fetchall()
    return answer_ids


@connection.connection_handler
def get_tag_by_question_id(cursor, id_):
    cursor.execute("""
                   SELECT * FROM question_tag
                   WHERE question_id=%(id_)s
                   """,
                   {'id_': id_})
    records = cursor.fetchall()
    return records


@connection.connection_handler
def insert_new_tag(cursor, new_tag):
    new_tag_name = new_tag['name']
    cursor.execute("""
                   INSERT INTO tag (name)
                   VALUES (%(new_tag_name)s)
                   """,
                   {'new_tag_name': new_tag_name})
    new_tag_id = get_max_id('tag')['max']
    new_tag_question_id = new_tag['question_id']
    cursor.execute("""
                   INSERT INTO question_tag (question_id, tag_id)
                   VALUES (%(new_tag_question_id)s, %(new_tag_id)s)
                   """,
                   {'new_tag_question_id': new_tag_question_id, 'new_tag_id': new_tag_id})


@connection.connection_handler
def delete_tags(cursor, question_id, tag):
    cursor.execute("""
                   DELETE FROM question_tag
                   WHERE question_id=%(question_id)s;
                   DELETE FROM tag
                   WHERE id=%(tag)s;
                   """,
                   {'question_id': question_id, 'tag': tag})


@connection.connection_handler
def update_tag(cursor, tag):
    tag_name = tag['name']
    tag_id = tag['tag_id']
    cursor.execute("""
                   UPDATE tag
                   SET name=%(tag_name)s
                   WHERE id=%(tag_id)s;
                   """,
                   {'tag_name': tag_name, 'tag_id': tag_id})


@connection.connection_handler
def get_basic_tags(cursor):
    cursor.execute("""
                   SELECT * FROM tag
                   WHERE id <= 9
                   """)
    basic_tags = cursor.fetchall()
    tag_s = []
    for tag in basic_tags:
        tag_s.append(tag['name'])
    return tag_s


def hash_password(password):
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password_hash = hashed_bytes.decode('utf-8')
    return password_hash


def verify_password(password, password_hash):
    hashed_bytes_password = password_hash.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_bytes_password)


@connection.connection_handler
def get_password_hash_by_name(cursor, name):
    cursor.execute("""
                   SELECT password_hash FROM user_account
                   WHERE name=%(name)s;
                   """,
                   {'name': name})
    password_hash = cursor.fetchone()['password_hash']
    return password_hash


@connection.connection_handler
def get_role_id_if_user_exists(cursor, name):
    cursor.execute("""
                   SELECT role_id FROM user_account
                   WHERE name=%(name)s;
                   """,
                   {'name': name})
    role_id = cursor.fetchone()
    return role_id['role_id'] if role_id else None


@connection.connection_handler
def register_user(cursor, name, password):
    role_id = get_role_id_if_user_exists(name)
    if role_id:
        return False
    else:
        password_hash = hash_password(password)
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
                       INSERT INTO user_account (name, password_hash, role_id, registration_date) VALUES (
                       %(name)s, %(password_hash)s, 2, %(registration_date)s);
                       """,
                       {'name': name, 'password_hash': password_hash, 'registration_date': registration_date})
        return True


@connection.connection_handler
def get_user_data(cursor, user_name):
    cursor.execute("""
                    SELECT user_account.id AS user_id, name, role, registration_date FROM user_account
                    JOIN user_role
                    ON role_id = user_role.id
                    WHERE name = %(user_name)s;
                    """,
                   {"user_name": user_name})
    user_data = cursor.fetchone()
    return user_data


@connection.connection_handler
def edit_user_data(cursor, u_name, what_to_do):
    if what_to_do == "delete":
        cursor.execute("DELETE FROM user_account WHERE name = %(u_name)s", {"u_name": u_name})


@connection.connection_handler
def get_all_user_data(cursor):
    cursor.execute("""SELECT name, role, registration_date FROM user_account
                    JOIN user_role
                    ON role_id = user_role.id;""")
    return cursor.fetchall()


@connection.connection_handler
def get_user_reputation(cursor, u_id):
    cursor.execute("""
                SELECT (answer.vote_number * 10) AS answer_votes,
                       (question.vote_number * 5) AS question_votes,
                       user_account.name AS user_name,
                       user_account.id AS user_id FROM question
                FULL JOIN answer
                ON answer.user_id = question.user_id
                FULL JOIN user_account
                ON question.user_id = user_account.id
                WHERE user_account.id = %(u_id)s
                AND (question.vote_number IS NOT NULL OR answer.vote_number IS NOT NULL);
                """, {"u_id": u_id})
    return cursor.fetchone()


@connection.connection_handler
def get_all_tags_questions(cursor):
    cursor.execute("""
                SELECT question.id AS question_id, title as question_title, name AS tag FROM question
                JOIN question_tag
                ON question.id = question_tag.question_id
                FULL JOIN tag
                ON tag_id = tag.id
                ORDER BY name DESC;
                """)
    return cursor.fetchall()


@connection.connection_handler
def get_user_id_by_user_name(cursor, name):
    cursor.execute("""
                   SELECT id FROM user_account
                   WHERE name=%(name)s
                   """,
                   {'name': name})
    user_id = cursor.fetchone()
    return user_id


@connection.connection_handler
def get_questions_by_user_id(cursor, user_id):
    cursor.execute("""
                   SELECT id, submission_time, view_number, vote_number,
                   title, message, image
                   FROM question
                   WHERE user_id = %(user_id)s
                   """,
                   {'user_id': user_id})
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_answers_by_user_id(cursor, user_id):
    cursor.execute("""
                   SELECT id, submission_time, vote_number, question_id,
                   message, image
                   FROM answer
                   WHERE user_id = %(user_id)s
                   """,
                   {'user_id': user_id})
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def get_comments_by_user_id(cursor, user_id):
    cursor.execute("""
                   SELECT id, question_id, answer_id, message,
                   submission_time, edited_count
                   FROM comment
                   WHERE user_id = %(user_id)s
                   """,
                   {'user_id': user_id})
    comments = cursor.fetchall()
    return comments
