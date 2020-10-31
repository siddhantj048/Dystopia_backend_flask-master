DROP TABLE IF EXISTS temp;

DROP TABLE IF EXISTS userauth;
CREATE TABLE userauth (firebase_uid text primary key not null,created_on datetime not null DEFAULT (datetime('now','localtime')));
DROP TABLE IF EXISTS contact;
CREATE TABLE contact(contact_id integer primary key not null , name text(100) not null,email text(200) not null ,message text,date TEXT not null DEFAULT (datetime('now','localtime')),CHECK(email LIKE '%___@___%')) ;

DROP TABLE IF EXISTS fosterer ;
CREATE TABLE fosterer(fosterer_id integer primary key not null, name text(100) not null,email text(200) not null,reason text not null,contact text(10) not null,animal_type text not null,foster_address text not null,foster_long real not null,foster_lat real not null ,CHECK (length(contact) >= 10 AND length(contact)<=12),CHECK(email LIKE '%___@___%') ) ;

DROP TABLE IF EXISTS photo;
CREATE TABLE photo(photo_id integer primary key not null,photo_url text not null)

DROP TABLE IF EXISTS animal;
CREATE TABLE animal(animal_id integer primary key ,owner_id text not null,name text(100) not null,age integer not null,gender text not null,breed text not null,descrip text not null,adopted integer not null default 0,approved integer not null default 0,house_trained integer not null default 0,neutered integer not null default 0,vaccines text default 'N.A',rehome_reason text not null,FOREIGN KEY(owner_id) REFERENCES userauth(firebase_uid) ON DELETE CASCADE) ;

DROP TABLE IF EXISTS animal_photo;
CREATE TABLE animal_photo(animal_id integer not null,photo_id integer not null,FOREIGN KEY(animal_id) REFERENCES animal(animal_id) ON DELETE CASCADE,FOREIGN KEY(photo_id) REFERENCES photo(photo_id))


DROP TABLE IF EXISTS user_profile;
CREATE TABLE user_profile(firebase_uid integer not null,profile_pic_id integer not null,name text(100) not null,dob text not null,contact text(10) not null,user_address text not null,user_long real not null,user_lat real not null,occupation text not null,email text(255) not null,FOREIGN KEY(profile_pic_id) REFERENCES photo(photo_id),FOREIGN KEY(firebase_uid) REFERENCES userauth(firebase_uid) ON DELETE CASCADE,CHECK (length(contact) >= 10 AND length(contact)<=12),CHECK(email LIKE '%___@___%'));

DROP TABLE IF EXISTS adopter ;
CREATE TABLE adopter(adopter_id text not null,animal_id integer not null,job_duration text,employer_contact text(10),experience text,day_time text not null,share_household text not null,house_type text not null,FOREIGN KEY(adopter_id) REFERENCES userauth(firebase_uid),FOREIGN KEY(animal_id) REFERENCES animal(animal_id) ON DELETE CASCADE,CHECK (length(employer_contact) >= 10 AND length(employer_contact)<=12));

DROP TABLE IF EXISTS blog;
CREATE TABLE blog(blog_id integer primary key,author text(200) not null default 'Anonymous',published_on text not null,content text not null,cover_photo_id integer not null,FOREIGN KEY(cover_photo_id) REFERENCES photo(photo_id))
