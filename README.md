# DOCUDB
Please Do Not Change Code Unless Asked!


Prerequisites for Running: Python 2.7.1

Summary of Project:
  This Project dealt with creating a document-oriented databse from scratch.  Everything in this repository was written by either Spencer or Ethan, including the parser.  We wanted to learn how to create a NoSQL database since we only ever worked with SQL databases in the past.  This database supports all of the operations of CRUD (Creation, Reading, Update, Deletion) and even supports where statements.  This project is the combined efforts of two Junior CS majors in a single term, from initial idea to final product.  It was not an easy task, but one that we are proud of because of that.
  

How To Use:

  Run Tests:
    In a terminal, go to the test directory, and type: python integration_test.py
    The tests should start running and printing either success or failure
    
  Run Manually Inputted Queries:
    In a terminal, go to src directiory, and type: python terminal.py
    Once it starts running, type queries as you want


Datatypes accepted:
Integers
Strings
Floats
Booleans
Referential Documents
Embedded Documents
Lists

Example queries to run:

create collection1

insert into collection1 "id1234" {name:"Ethan",age:20.888,cool  :true ,children :6   }
insert into collection1 "id1235" {name:"Specer",age:25.888,cool  :true ,children :100 , wives : "at least 23"   }


select * from collection1 
select _key from collection1
select name from collection1 

select * from collection1 where (_key == "id1235")

select * from collection1 where (_key == "id1234" and name == "Ethan")

select * from collection1 where (name == "Specer")


update collection1 set [age, children] = [21, 0] where (_key == "id1234")

update collection1 set [age] = [21.] where (_key == "id1234")

upsert collection1 set [job] = ["Cleaner"] where (_key == "id1234")

delete name from collection1

delete * from collection1
delete * from collection1 where (_key == "id1234")

drop collection1



drop c_emb
create c_emb

Embedded Document special syntax:
insert into c_emb "id1" {name: "joe", child : {_key : "sid1", name : "Jonny", age : 3}, pay : 90000} 
Reference Document special syntax:
insert into c_emb "id2" {name: "dick", child : <c_emb, child1>, pay : 90000} 
List Special Syntax:
insert into c_emb "id3" {name: "joe", children: [{_key : "sid1", name : "Jonny", age : 3}, {_key : "sid2", name : "Jon", age : 6}, 666], pay : 90000} 


update c_emb set [name] = ["CLONE"] 



select * from c_emb 




Notes on Databse including restraints and picture of parsing tree if people are curious:
https://docs.google.com/document/d/1FQ1Hc2AMHHdax1Fot6NV-0GvFYed6kyF3Xe6c5kFlQs/edit?usp=sharing
