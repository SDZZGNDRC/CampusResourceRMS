# CampusResourceRMS
This system aims to provide a unified reservation management platform for various school resources (e.g. classrooms in academic buildings, discussion rooms in libraries, activity rooms in activity centers, gymnasiums in stadiums, and laboratories, etc.).


## Table design

### User

1. userID (Primary Key)
2. username
3. hashed_password
4. email
5. roleID (Foreign Key)
6. studentID (nullable)
7. teacherID (nullable)

### ResourceType

1. resourceTypeID (Primary Key)
2. name
3. description

### Resource

1. resourceID (Primary Key)
2. resourceTypeID (Foreign Key)
3. name
4. description (nullable)
5. location (nullable)
6. capacity
7. status
8. responsibleID (Foreign Key) (nullable)

### Reservation

1. reservationID (Primary Key)
2. startTime
3. endTime
4. resourceID (Foreign Key)
5. status
6. description (nullable)

### Role

1. roleID (Primary Key)
2. name
3. description

### UsageRecord

1. usageRecordID (Primary Key)
2. reservationID (Foreign Key)
3. userID (Foreign Key)






