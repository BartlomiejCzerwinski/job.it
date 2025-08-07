# Generate Sample Candidates Command

This Django management command generates sample candidate (worker) profiles for testing and development purposes.

## Usage

### Basic Usage
Generate 10 sample candidate profiles (default):
```bash
python manage.py generate_sample_candidates
```

### Generate Specific Number of Profiles
Generate 25 candidate profiles:
```bash
python manage.py generate_sample_candidates --count 25
```

### Clear Existing Profiles Before Creating New Ones
Remove all existing worker profiles and create new ones:
```bash
python manage.py generate_sample_candidates --clear --count 15
```

## What Gets Generated

Each candidate profile includes:

1. **Basic Information**
   - First and last name
   - Email address
   - Position (e.g., Full Stack Developer, Data Scientist, etc.)
   - Phone number
   - Location (country and city)
   - Work preferences (remote/hybrid)
   - Availability (ASAP, 2 weeks, 1 month, 3 months)

2. **Professional Details**
   - About Me section with personalized description
   - 5-12 random skills with different proficiency levels:
     - Level 1: Beginner
     - Level 2: Intermediate  
     - Level 3: Advanced

3. **Social Links** (2-4 random platforms)
   - GitHub
   - LinkedIn
   - Personal website
   - Stack Overflow

4. **Projects** (1-3 sample projects)
   - Project title
   - Description
   - Technologies used
   - Optional GitHub link
   - Optional demo link

## Default Credentials

All generated test users have the same password for easy testing:
- **Password**: `password123`

## Examples

### Generate 50 test candidates
```bash
python manage.py generate_sample_candidates --count 50
```

### Reset database with fresh test data
```bash
python manage.py generate_sample_candidates --clear --count 20
```

## Notes

- The command checks for existing emails to avoid duplicates
- Skills must be loaded in the database first (from skills.csv)
- Locations are created automatically if they don't exist
- All generated users have the role 'worker' (not 'recruiter')

## Sample Data Characteristics

The command generates realistic-looking profiles with:
- Common first and last names
- Professional positions relevant to IT/tech industry
- Mix of experience levels (1-15 years)
- Various specializations (web development, mobile apps, cloud, ML, etc.)
- Realistic project descriptions
- Proper formatting for phone numbers (xxx xxx xxx)
- Valid-looking social media URLs

