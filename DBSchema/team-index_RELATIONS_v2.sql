CREATE TABLE Users (
    user_id VARCHAR,
    uname VARCHAR NOT NULL,
    average_stars INTEGER,
    fans INTEGER,
    cool INTEGER,
    tipCount INTEGER,
    funny INTEGER,
    totalLikes INTEGER,
    useful INTEGER,
    user_latitude DECIMAL,
    user_longitude DECIMAL,
    yelping_since DATE NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE Friends (
    user_id VARCHAR,
    friend_id VARCHAR,
    PRIMARY KEY (user_id, friend_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Business (
    business_id VARCHAR,
    bname VARCHAR NOT NULL,
    city VARCHAR,
    state VARCHAR,
    zipcode INTEGER,
    latitude DECIMAL,
    longitude DECIMAL,
    address VARCHAR,
    numTips INTEGER,
    numCheckins INTEGER,
    is_open BOOLEAN,
    stars DECIMAL,
    PRIMARY KEY (business_id)
);

CREATE TABLE Tip (
    user_id VARCHAR,
    business_id VARCHAR,
    tipDate TIMESTAMP NOT NULL,
    tipText VARCHAR,
    likes INTEGER,
    PRIMARY KEY(user_id, tipDate, business_id),
    FOREIGN KEY(user_id) REFERENCES Users(user_id),
    FOREIGN KEY(business_id) REFERENCES Business(business_id)
);

CREATE TABLE Categories (
  business_id VARCHAR,
  category_name VARCHAR,
  PRIMARY KEY (business_id, category_name),
  FOREIGN KEY (business_id) REFERENCES Business(business_id)
);


CREATE TABLE Attributes (
  business_id VARCHAR,
  attr_name VARCHAR,
  value VARCHAR,
  PRIMARY KEY (business_id, attr_name),
  FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE Hours (
  business_id VARCHAR,
  dayOfWeek VARCHAR,
  close VARCHAR,
  open VARCHAR,
  PRIMARY KEY (business_id, dayOfWeek),
  FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE Checkins (
  business_id VARCHAR,
  year VARCHAR,
  month VARCHAR,
  day VARCHAR,
  time TIME,
  PRIMARY KEY (business_id, year, month, day, time),
  FOREIGN KEY (business_id) REFERENCES Business(business_id)
);
