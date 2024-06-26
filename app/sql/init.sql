-- Check if the "admin" role already exists
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'admin') THEN
CREATE ROLE admin LOGIN PASSWORD 'POSTGRES_PASSWORD';
ALTER ROLE admin WITH SUPERUSER;
END IF;
END $$;

-- CREATE TABLE IF NOT EXISTS users (user_id serial PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS surgeries (id serial PRIMARY KEY, surgery VARCHAR(100) NOT NULL, surgery_description VARCHAR(100) NOT NULL );
CREATE TABLE IF NOT EXISTS tier_lists (
                                          id serial PRIMARY KEY,
                                          tier VARCHAR(50) NOT NULL,
                                          surgery_id INTEGER REFERENCES surgeries(id),
                                          visa_sponsorship VARCHAR(100) NOT NULL,
                                          flight_type VARCHAR(100) NOT NULL,
                                          number_family_members VARCHAR(100) NOT NULL,
                                          hospital_accomodations VARCHAR(100) NOT NULL,
                                          hotel VARCHAR(100) NOT NULL,
                                          duration_stay VARCHAR(100) NOT NULL,
                                          tourism_package VARCHAR(100) NOT NULL,
                                          post_surgery_monitoring VARCHAR(100) NOT NULL,
                                          price VARCHAR(40) NOT NULL
);

-- -- Users Table
-- INSERT INTO users (name) VALUES ('user1');

-- Surgeries Table
INSERT INTO surgeries (surgery, surgery_description)
VALUES ('CABG - Coronary artery bypass graft of 3 or more vessels', 'Surgical procedure to treat coronary artery disease');

-- Tier List table
-- CABG - Coronary artery bypass graft of 3 or more vessels
INSERT INTO tier_lists(tier, surgery_id, visa_sponsorship, flight_type, number_family_members, hospital_accomodations, hotel, duration_stay, tourism_package, post_surgery_monitoring, price)
VALUES ('Standard', 1, 'Support for obtaining a visa', 'Travel in economy class',
        'No family members','Bed in infarmary', '3/4 star hotel', 'Shortest possible stay',
        'No tourism package', 'Follow-up until the date of travel home', '45000€');

INSERT INTO tier_lists(tier, surgery_id, visa_sponsorship, flight_type, number_family_members,
                       hospital_accomodations, hotel, duration_stay, tourism_package, post_surgery_monitoring, price)
VALUES ('Premium', 1, 'Support for obtaining a visa', 'Travel in Business class',
        'Possibility of bringing a companion','Private bedroom in the hospital', '5 star hotel', 'Extended stay', 'Tourism package',
        'Monitoring the client in the country of origin up to 2 months after surgery', '70000€');

INSERT INTO tier_lists(tier, surgery_id, visa_sponsorship, flight_type, number_family_members, hospital_accomodations,
                       hotel, duration_stay, tourism_package, post_surgery_monitoring, price)
VALUES ('Deluxe', 1, 'Support for obtaining a visa', 'Travel in First class',
        'Possibility of bringing 3 companions','Bed in private room with suite', '5 star hotel',
        'Extended stay (minimum 15 days) ', 'Tourism package for client and companions, with national trips and itineraries',
        'Monitoring the client in the country of origin up to 6 months after surgery', '130000€');
