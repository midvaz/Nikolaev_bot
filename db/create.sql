
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE,
    chat_id INT,
    is_admin BOOlEAN,
    user_name TEXT
);

CREATE TABLE IF NOT EXISTS wallets(
    id SERIAL PRIMARY KEY,
    user_id INT,
    chain TEXT,
    wallet TEXT,
    w_name TEXT,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS trackingflags (
    user_flag_id INT,
    flag BOOlEAN,
    FOREIGN KEY (user_flag_id) REFERENCES users(user_id)
);