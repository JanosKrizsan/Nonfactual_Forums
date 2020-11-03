# Nonfactual Forums

![Forum Romanum](https://i.imgur.com/D3co38w.jpg)

## What is this?

It is a lightweight, non-JavaScript forum with features akin to any regular forum. There is user authentication, they can ask and reply to questions / topics, add or remove tags and vote. This is a reupload of older code.

## Tech Used

- Python with Flask
- HTML & CSS
- PostgreSQL

## Features

- PSQL Database
- Can post questions
- Can post answers
- Can upvote / downvote
- Can add tags to posts
- Registration and login / logout
- Able to edit or delete already made posts

## Code Example

A simple query of inserting a new record into the database.
```
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
```

## Contributors

[David Schmidt](https://github.com/DavidAdamSchmidt)<br>
[Barnabas Matrai](https://github.com/barnabasMatrai)<br>
[Janos Krizsan](https://github.com/JanosKrizsan)
