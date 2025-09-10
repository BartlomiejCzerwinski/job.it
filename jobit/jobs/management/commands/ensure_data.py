                    full_name=f'Recruiter {i+1} Smith',
                    role='recruiter',
                    position='HR Manager'
                )
                recruiters.append(app_user)
            else:
                recruiters.append(User.objects.get(email=email).appuser)
        
        # Get or create a location
        location, _ = Location.objects.get_or_create(country='Poland', city='Warsaw')
        
        created = 0
        for i in range(count):
            if self.timeout_occurred:
                break
                
            try:
                job_title = random.choice(job_titles)
                company = random.choice(companies)
                recruiter = random.choice(recruiters)
                
                # Create job
                job = JobListing.objects.create(
                    job_title=job_title,
                    company_name=company,
                    about_company=f'{company} is a great company to work for',
                    job_description=f'We need an experienced {job_title} to join our team',
                    salary_min=random.randint(4000, 8000),
                    salary_max=random.randint(8000, 15000),
                    salary_currency='PLN',
                    location=location,
                    job_model=random.choice(['REMOTE', 'HYBRID', 'STATIONARY']),
                    owner=recruiter,
                    status='ACTIVE'
                )
                
                # Add 3-5 random skills
                skills = list(Skill.objects.all())
                if skills:
                    num_skills = random.randint(3, min(5, len(skills)))
                    selected_skills = random.sample(skills, num_skills)
                    for skill in selected_skills:
                        JobListingSkill.objects.create(
                            job_listing=job,
                            skill=skill,
                            level=random.randint(1, 5)
                        )
                
                created += 1
                self.stdout.write(f'✅ Created: {job_title} at {company}')
                
            except Exception as e:
                self.stdout.write(f'❌ Failed to create job {i+1}: {str(e)}')
                continue
        
        self.stdout.write(f'💼 Created {created} job listings')
