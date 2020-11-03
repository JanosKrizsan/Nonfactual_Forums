--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.6
-- Dumped by pg_dump version 9.5.6

ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS pk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS fk_question_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS pk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_answer_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS pk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_comment_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS pk_question_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.tag DROP CONSTRAINT IF EXISTS pk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.user_role DROP CONSTRAINT IF EXISTS pk_role_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.user_account DROP CONSTRAINT IF EXISTS pk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.user_account DROP CONSTRAINT IF EXISTS fk_role_id CASCADE;

DROP TABLE IF EXISTS public.question;
DROP SEQUENCE IF EXISTS public.question_id_seq;
CREATE TABLE question (
    id serial NOT NULL,
    user_id integer,
    submission_time timestamp without time zone,
    view_number integer,
    vote_number integer,
    title text,
    message text,
    image text
);

DROP TABLE IF EXISTS public.answer;
DROP SEQUENCE IF EXISTS public.answer_id_seq;
CREATE TABLE answer (
    id serial NOT NULL,
    user_id integer,
    submission_time timestamp without time zone,
    vote_number integer,
    question_id integer,
    message text,
    image text
);

DROP TABLE IF EXISTS public.comment;
DROP SEQUENCE IF EXISTS public.comment_id_seq;
CREATE TABLE comment (
    id serial NOT NULL,
    user_id integer,
    question_id integer,
    answer_id integer,
    message text,
    submission_time timestamp without time zone,
    edited_count integer
);


DROP TABLE IF EXISTS public.question_tag;
CREATE TABLE question_tag (
    question_id integer NOT NULL,
    tag_id integer NOT NULL
);

DROP TABLE IF EXISTS public.tag;
DROP SEQUENCE IF EXISTS public.tag_id_seq;
CREATE TABLE tag (
    id serial NOT NULL,
    name text
);

DROP TABLE IF EXISTS public.user_role;
DROP SEQUENCE IF EXISTS public.user_role_id_seq;
CREATE TABLE user_role (
    id serial NOT NULL,
    role text
);

DROP TABLE IF EXISTS public.user_account;
DROP SEQUENCE IF EXISTS public.user_account_id_seq;
CREATE TABLE user_account (
    id serial NOT NULL,
    name text,
    password_hash text,
    role_id integer,
    registration_date timestamp without time zone
);

ALTER TABLE ONLY question
    ADD CONSTRAINT pk_question_id PRIMARY KEY (id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT pk_answer_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT pk_comment_id PRIMARY KEY (id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT pk_question_tag_id PRIMARY KEY (question_id, tag_id);

ALTER TABLE ONLY tag
    ADD CONSTRAINT pk_tag_id PRIMARY KEY (id);

ALTER TABLE ONLY user_role
    ADD CONSTRAINT pk_role_id PRIMARY KEY (id);

ALTER TABLE ONLY user_account
    ADD CONSTRAINT pk_user_id PRIMARY KEY (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT fk_question_user_id FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE;

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE;

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_answer_user_id FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE;

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE;

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id) ON DELETE CASCADE;

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_comment_user_id FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE;

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE;

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE;

ALTER TABLE ONLY user_account
    ADD CONSTRAINT fk_role_id FOREIGN KEY (role_id) REFERENCES user_role(id) ON DELETE CASCADE;

ALTER TABLE ONLY user_account
    ADD CONSTRAINT un_user_name UNIQUE (name);

INSERT INTO user_role VALUES (1, 'admin');
INSERT INTO user_role VALUES (2, 'user');
SELECT pg_catalog.setval('user_role_id_seq', 2, true);

INSERT INTO user_account VALUES (1, 'Godmin', '$2b$12$brBXWIaNLmvWMGXtXAtx6.Pfk.aA7YuU3C3WFVtZ4UOaRv5WsoSnG', 1, '2017-03-25 17:49:00');
INSERT INTO user_account VALUES (2, 'george2000', '$2b$12$E2PoOy8Mr29wSi6bCYac5emal5Jy4zzSNlWGn/HApiWBPsb1opG3.', 2, '2017-03-26 11:33:00');
INSERT INTO user_account VALUES (3, 'iam_the_one', '$2b$12$jPBG45921ECqAUhSSn.29.43orOytQ7O/DgsrlA.7T5r4LK5YblmG', 2, '2017-03-28 19:02:00');
INSERT INTO user_account VALUES (4, 'randomguy', '$2b$12$3zE1mU3BrlC8fkd11a2Rbu.pp.HU7RrBZ4hHt94lJt3/37VxGzsgu', 2, '2017-03-28 19:48:00');
INSERT INTO user_account VALUES (5, 'pythonpro', '$2b$12$sZC6lS8beSsUUJHc.KbW3uQpAwuglGdoO.f0ChL6rvP3kFxIrpkWq', 2, '2017-03-28 21:27:00');
INSERT INTO user_account VALUES (6, 'gotsucks', '$2b$12$zmh6ghwMSScDAiSuKMhxTuNlMdDWjumo1gelgQHpJ2w1EtBkZcQwa', 2, '2017-03-29 03:05:00');
SELECT pg_catalog.setval('user_account_id_seq', 6, true);

INSERT INTO question VALUES (1, 4, '2017-04-28 08:29:00', 29, 7, 'How to make lists in Python?', 'I am totally new to this, any hints?', NULL);
INSERT INTO question VALUES (2, 6, '2017-04-29 09:19:00', 15, 9, 'Wordpress loading multiple jQuery Versions', 'I developed a plugin that uses the jquery booklet plugin (http://builtbywill.com/booklet/#/) this plugin binds a function to $ so I cann call $(".myBook").booklet();

I could easy managing the loading order with wp_enqueue_script so first I load jquery then I load booklet so everything is fine.

BUT in my theme i also using jquery via webpack so the loading order is now following:

jquery
booklet
app.js (bundled file with webpack, including jquery)', 'image1.png');
INSERT INTO question VALUES (3, 2, '2017-05-01 10:41:00', 1364, 57, 'Drawing canvas with an image picked with Cordova Camera Plugin', 'I''m getting an image from device and drawing a canvas with filters using Pixi JS. It works all well using computer to get an image. But when I''m on IOS, it throws errors such as cross origin issue, or that I''m trying to use an unknown format.', NULL);
SELECT pg_catalog.setval('question_id_seq', 3, true);

INSERT INTO answer VALUES (1, 3, '2017-04-28 16:49:00', 4, 1, 'You need to use brackets: my_list = []', NULL);
INSERT INTO answer VALUES (2, 5, '2017-04-25 14:42:00', 35, 1, 'Look it up in the Python docs', 'image2.jpg');
SELECT pg_catalog.setval('answer_id_seq', 2, true);

INSERT INTO comment VALUES (1, 6, 1, NULL, 'Please clarify the question as it is too vague!', '2017-05-01 05:49:00');
INSERT INTO comment VALUES (2, 2, NULL, 1, 'I think you could use my_list = list() as well.', '2017-05-02 16:55:00');
SELECT pg_catalog.setval('comment_id_seq', 2, true);

INSERT INTO tag VALUES (1, 'Python');
INSERT INTO tag VALUES (2, 'SQL');
INSERT INTO tag VALUES (3, 'CSS');
INSERT INTO tag VALUES (4, 'HTML');
INSERT INTO tag VALUES (5, 'JavaScript');
INSERT INTO tag VALUES (6, 'Java');
INSERT INTO tag VALUES (7, 'C#');
INSERT INTO tag VALUES (8, 'C++');
INSERT INTO tag VALUES (9, 'C');
INSERT INTO tag VALUES (10, 'jQuery');
SELECT pg_catalog.setval('tag_id_seq', 10, true);

INSERT INTO question_tag VALUES (1, 1);
INSERT INTO question_tag VALUES (2, 10);
INSERT INTO question_tag VALUES (3, 5);