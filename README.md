# HackI/O

local database set up
1. Download python libraries
2. download Postgre SQL (newest version with default everything)
3. make intial root user 'postgres' with password 'postgres'
4. make note of what port is being used default is 5432 but it could be 5433
5. my path variable called 'DATABASE_URL' with value 'postgresql+psycopg2: //postgres:postgres@localhost:5432/testdb'
6. launch pgAdmin
7. create a new role with your windows account name with no password and all permissions