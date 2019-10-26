create database emaildb;
drop database if exists email_sender;

\c emaildb

CREATE TABLE emails (
    id serial not null,
    data timestamp not null DEFAULT CURRENT_TIMESTAMP,
    assunto varchar(100) not null,
    mensagem varchar(255) not null
);