"""
Data-driven career domain registry.

Each entry defines: keywords to match, exclusions to avoid false positives,
priority (higher = checked first), and the career data to return.
To add a new career domain, simply append a new dict to this list.
"""

CAREER_DOMAINS = [
    # --- 1. Healthcare, Diagnostics & Allied Health ---
    {
        'keywords': ['dentist', 'dental', 'teeth', 'tooth', 'oral health', 'dental surgeon', 'orthodontist'],
        'priority': 90,
        'data': {
            'career_name': 'Dental Surgeon / Dentist',
            'career_description': 'Dental Surgeons diagnose oral health disorders, treat teeth decay, perform maxillofacial surgeries, and manage cosmetic dental care.',
            'primary_keywords': ['Dental Surgery', 'Human Biology', 'Medicine', 'BDS'],
            'secondary_keywords': ['Chemistry', 'Biology', 'Health'],
            'explanations': {
                'Dental Surgery': 'Direct Bachelor of Dental Surgery (BDS) professional degree.',
                'Human Biology': 'Pre-clinical biological foundation for dental surgery.',
                'Medicine': 'Covers systemic clinical pathology and medical sciences.'
            }
        }
    },
    {
        'keywords': ['sonograph', 'radiograph', 'ultrasound', 'x-ray', 'medical imaging', 'mri', 'ct scan'],
        'priority': 90,
        'data': {
            'career_name': 'Diagnostic Radiographer / Medical Sonographer',
            'career_description': 'Radiographers and Sonographers operate advanced diagnostic imaging machinery including MRI, CT, and Ultrasound to detect diseases and internal injuries.',
            'primary_keywords': ['Medical Imaging', 'Medical Laboratory', 'Human Biology'],
            'secondary_keywords': ['Physics', 'Biology', 'Health'],
            'explanations': {
                'Medical Imaging': 'Direct degree program in radiography, ultrasound sonography, and diagnostic imaging.',
                'Medical Laboratory': 'Clinical diagnostic foundations and pathology.'
            }
        }
    },
    {
        'keywords': ['optometrist', 'optometry', 'eye', 'vision', 'glasses'],
        'exclude': ['television', 'division', 'provision'],
        'priority': 90,
        'data': {
            'career_name': 'Optometrist',
            'career_description': 'Optometrists diagnose, treat, and manage visual disorders and ocular health conditions.',
            'primary_keywords': ['Optometry', 'Human Biology', 'Medical Imaging'],
            'secondary_keywords': ['Medical', 'Biology', 'Health'],
            'explanations': {
                'Optometry': 'Direct Doctor of Optometry degree program for vision care specialists.'
            }
        }
    },
    {
        'keywords': ['speech therap', 'audiolog', 'hearing', 'speech pathologist', 'stutter', 'speech impairment'],
        'priority': 90,
        'data': {
            'career_name': 'Speech Therapist / Audiologist',
            'career_description': 'Speech Therapists and Audiologists diagnose and treat speech, language, swallowing, and hearing disorders across children and adults.',
            'primary_keywords': ['Special Education', 'Human Biology', 'Nursing', 'Education'],
            'secondary_keywords': ['Biology', 'English', 'Linguistics'],
            'explanations': {
                'Special Education': 'Direct academic pathway specializing in hearing, speech, and developmental communications.',
                'Human Biology': 'Provides physiological and neuro-biological foundations.'
            }
        }
    },
    {
        'keywords': ['occupational health', 'workplace safety', 'ergonom', 'industrial hazard', 'safety officer', 'osha'],
        'priority': 85,
        'data': {
            'career_name': 'Occupational Health & Safety Officer',
            'career_description': 'Occupational Health and Safety Officers inspect industrial workplaces, identify hazardous machinery risks, design fire safety protocols, and prevent occupational injuries.',
            'primary_keywords': ['Public Health', 'Environmental Science', 'Civil Engineering', 'Mechanical Engineering'],
            'secondary_keywords': ['Physics', 'Chemistry', 'Biology'],
            'explanations': {
                'Public Health': 'Occupational epidemiology, workplace toxicology, and safety regulations.',
                'Environmental Science': 'Hazardous waste control and environmental risk management.'
            }
        }
    },
    {
        'keywords': ['public health', 'epidemiolog', 'disease outbreak', 'vaccination', 'community hygien', 'sanitation officer'],
        'priority': 85,
        'data': {
            'career_name': 'Public Health Officer & Epidemiologist',
            'career_description': 'Public Health Officers and Epidemiologists track infectious disease epidemics, lead community vaccination drives, and establish municipal sanitation standards.',
            'primary_keywords': ['Public Health', 'Water and Public Health Engineering', 'Nursing', 'Biological Science'],
            'secondary_keywords': ['Chemistry', 'Biology', 'Statistics'],
            'explanations': {
                'Public Health': 'Direct degree program in epidemiology, biostatistics, and disease prevention.',
                'Water and Public Health Engineering': 'Covers potable water safety, sanitation infrastructure, and municipal health.'
            }
        }
    },
    {
        'keywords': ['veterinary', 'veterinarian', 'animal doctor', 'pet doctor', 'animal healthcare', 'treat animals'],
        'regex_patterns': [r'\bvets?\b'],
        'priority': 85,
        'data': {
            'career_name': 'Veterinary Doctor / Animal Health Specialist',
            'career_description': 'Veterinary Doctors diagnose illnesses in domestic, farm, and wild animals, perform surgeries, prescribe medications, and safeguard animal welfare and zoonotic disease control.',
            'primary_keywords': ['Veterinary', 'Doctor of Veterinary Medicine', 'Animal Science', 'Agriculture'],
            'secondary_keywords': ['Biological Science', 'Biochemistry', 'Chemistry', 'Biology'],
            'explanations': {
                'Veterinary': 'Direct Doctor of Veterinary Medicine (DVM) degree preparing licensed veterinary physicians.',
                'Animal Science': 'Covers livestock physiology, animal nutrition, breeding, and health management.',
                'Agriculture': 'Provides broad agricultural, livestock production, and bio-science foundations.'
            }
        }
    },
    {
        'keywords': ['forensic', 'crime scene', 'criminology', 'investigate crime', 'solve murder', 'police investigator', 'crime lab'],
        'priority': 85,
        'data': {
            'career_name': 'Forensic Scientist / Crime Lab Analyst',
            'career_description': 'Forensic Scientists analyze chemical traces, biological fluids, DNA profiles, and physical evidence from crime scenes to support criminal justice investigations.',
            'primary_keywords': ['Medical Laboratory', 'Biochemistry', 'Chemistry', 'Biological Science', 'Law'],
            'secondary_keywords': ['Physics', 'General Science'],
            'explanations': {
                'Medical Laboratory': 'Diagnostic lab pathology, toxicology testing, and clinical sample analysis.',
                'Biochemistry': 'Provides deep chemical and DNA profiling foundations essential for forensic investigation.',
                'Chemistry': 'Covers analytical chemistry, substance identification, and laboratory forensics.'
            }
        }
    },
    {
        'keywords': ['dietetic', 'dietitian', 'nutritionist', 'nutrition', 'clinical diet'],
        'priority': 85,
        'data': {
            'career_name': 'Clinical Dietitian / Nutrition Specialist',
            'career_description': 'Dietitians and Nutritionists assess nutritional needs, formulate clinical diets, manage metabolic disorders, and promote public nutritional wellness.',
            'primary_keywords': ['Dietetics', 'Food Science and Technology', 'Human Nutrition', 'Nutrition'],
            'secondary_keywords': ['Chemistry', 'Biology', 'Health'],
            'explanations': {
                'Dietetics': 'Direct clinical degree in therapeutic nutrition and clinical dietetics.',
                'Food Science and Technology': 'Covers food chemistry, nutritional processing, and food safety.'
            }
        }
    },
    {
        'keywords': ['pharmacy', 'pharmacist', 'pharmacology', 'drug discovery', 'pharmd', 'prescribe medications', 'compound and dispense'],
        'priority': 85,
        'data': {
            'career_name': 'Pharmacist',
            'career_description': 'Pharmacists compound, dispense, and monitor pharmaceutical medications for patient treatment.',
            'primary_keywords': ['Pharmacy', 'Doctor of Pharmacy', 'Biochemistry'],
            'secondary_keywords': ['Chemistry', 'Biochemistry', 'Health'],
            'explanations': {
                'PharmD': 'Direct Doctor of Pharmacy degree program.',
                'Pharmacy': 'Direct pharmaceutical sciences degree.'
            }
        }
    },
    {
        'keywords': ['nurse', 'nursing', 'midwife', 'midwifery', 'bedside patient', 'deliver newborn', 'pregnant mother'],
        'priority': 80,
        'data': {
            'career_name': 'Registered Nurse / Midwife',
            'career_description': 'Registered Nurses and Midwives provide primary patient care, clinical treatments, and maternal healthcare across hospitals and community health centers.',
            'primary_keywords': ['Nursing', 'Midwifery', 'Nurse'],
            'secondary_keywords': ['Health', 'Medical', 'Biology'],
            'explanations': {
                'Nursing': 'Direct degree program training students in clinical nursing skills and patient care.',
                'Midwifery': 'Direct degree program specializing in maternal and infant healthcare.',
                'Health': 'Provides foundational medical and health sciences preparation.'
            }
        }
    },
    {
        'keywords': ['physiotherap', 'physical therapy', 'stroke patient', 'rehabilitat'],
        'priority': 80,
        'data': {
            'career_name': 'Physiotherapist / Physical Rehabilitation Specialist',
            'career_description': 'Physiotherapists assess, treat, and rehabilitate patients with movement disorders, sports injuries, neurological conditions, and physical disabilities.',
            'primary_keywords': ['Physiotherapy', 'Physical Therapy', 'Sports Science'],
            'secondary_keywords': ['Biology', 'Physics', 'Health', 'Medical'],
            'explanations': {
                'Physiotherapy': 'Direct clinical degree preparing physical rehabilitation and movement specialists.',
                'Physical Therapy': 'Direct degree path in physical rehabilitation.'
            }
        }
    },
    {
        'keywords': ['microbio', 'bacteria', 'virus', 'fungi', 'infectious microbe', 'pathogen', 'microscopic virus'],
        'priority': 80,
        'data': {
            'career_name': 'Microbiologist & Pathogen Specialist',
            'career_description': 'Microbiologists investigate bacteria, viruses, fungi, and microscopic parasites to develop antibiotics, control disease transmission, and support food fermentation.',
            'primary_keywords': ['Biological Science', 'Biochemistry', 'Medical Laboratory', 'Biotechnology'],
            'secondary_keywords': ['Biology', 'Chemistry'],
            'explanations': {
                'Biological Science': 'Covers microbiology, pathogen life cycles, and cellular biology.',
                'Medical Laboratory': 'Diagnostic lab pathology and clinical pathogen culturing.'
            }
        }
    },
    {
        'keywords': ['biochem', 'protein', 'enzyme', 'molecular bio', 'biotechnol', 'recombinant protein'],
        'priority': 80,
        'data': {
            'career_name': 'Biochemist & Molecular Biologist',
            'career_description': 'Biochemists and Molecular Biologists analyze cellular chemical processes, genetically engineered proteins, enzyme kinetics, and biotech therapeutics.',
            'primary_keywords': ['Biochemistry', 'Biotechnology', 'Biological Science', 'Medical Laboratory'],
            'secondary_keywords': ['Chemistry', 'Biology', 'Science'],
            'explanations': {
                'Biochemistry': 'Direct degree exploring molecular biology and chemical processes in living organisms.',
                'Biotechnology': 'Specialized path for industrial bio-processing and genetic engineering.'
            }
        }
    },
    {
        'keywords': ['dna', 'genetics', 'medical laboratory', 'biomedical', 'laboratory disease', 'clinical lab', 'pathology', 'blood sample', 'lab specimen'],
        'priority': 80,
        'data': {
            'career_name': 'Biomedical Scientist / Medical Lab Specialist',
            'career_description': 'Biomedical Scientists conduct clinical diagnostic laboratory tests, investigate disease mechanisms, analyze genetic markers, and develop medical therapies.',
            'primary_keywords': ['Medical Laboratory', 'Biomedical Science', 'Biochemistry', 'Biological Science', 'Molecular'],
            'secondary_keywords': ['Chemistry', 'Biology', 'Health'],
            'explanations': {
                'Medical Laboratory': 'Direct clinical degree for diagnostic testing, pathology analysis, and lab practice.',
                'Biomedical Science': 'Prepares students for advanced biomedical research and therapeutic development.',
                'Biochemistry': 'Provides deep chemical and molecular understanding of biological systems.'
            }
        }
    },
    {
        'keywords': ['health field', 'healthcare', 'health care', 'health sector', 'allied health', 'health science', 'health sciences', 'health career', 'medical field', 'allied health hospital units'],
        'priority': 50,
        'data': {
            'career_name': 'Healthcare & Allied Health Practitioner',
            'career_description': 'Healthcare and Allied Health specialists deliver clinical nursing, rehabilitation therapy, medical diagnostics, nutritional guidance, healthcare data systems, and public health disease prevention across hospitals and community health centres.',
            'primary_keywords': ['Nursing', 'Midwifery', 'Physiotherapy', 'Dietetics', 'Health Information', 'Public Health', 'Water and Public Health Engineering', 'Medical Laboratory', 'Medical Imaging', 'Public Health Nursing'],
            'secondary_keywords': ['Biology', 'Chemistry', 'Health', 'General Science'],
            'explanations': {
                'Nursing': 'Direct degree program training students in clinical nursing skills and hospital patient care.',
                'Midwifery': 'Direct degree specializing in maternal, prenatal, and infant healthcare.',
                'Physiotherapy': 'Specialized clinical path in physical rehabilitation and movement recovery therapy.',
                'Dietetics': 'Specialized clinical path focusing on human nutrition, dietary planning, and metabolic health.',
                'Health Information': 'Covers medical records informatics, health statistics, and healthcare data systems.',
                'Public Health': 'Focuses on epidemiology, community hygiene, sanitation, and disease prevention programs.',
                'Water and Public Health Engineering': 'Direct engineering degree for potable water supply, environmental health, and municipal sanitation.',
                'Medical Laboratory': 'Direct clinical diagnostic pathology and laboratory disease analysis.'
            }
        }
    },
    {
        'keywords': ['doctor', 'medicine', 'physician', 'surgeon', 'surgery', 'surgeries', 'surgical', 'operating room', 'treat sick', 'sick people', 'sick person', 'treating sick', 'cure disease', 'cure patient', 'cure infection', 'treat patient', 'treating patient', 'heal sick', 'heal people', 'heal critical patients', 'hospital medicine', 'mbchb'],
        'regex_patterns': [r'\bcures?\b'],
        'priority': 70,
        'data': {
            'career_name': 'Medical Doctor / Physician',
            'career_description': 'Medical Doctors diagnose diseases, prescribe medical treatments, and perform clinical care across hospitals.',
            'primary_keywords': ['Medicine', 'Surgery', 'Human Biology', 'Medical Laboratory'],
            'secondary_keywords': ['Health', 'Biomedical', 'Biology'],
            'explanations': {
                'Medicine': 'Direct MBChB degree program preparing medical doctors for clinical practice.',
                'Surgery': 'Core clinical component of medical doctor training.',
                'Human Biology': 'Pre-clinical undergraduate degree path for medical studies.'
            }
        }
    },

    # --- 2. Computing, AI, Robotics & Tech ---
    {
        'keywords': ['blockchain', 'crypto', 'smart contract', 'fintech', 'distributed ledger', 'dapps'],
        'priority': 85,
        'data': {
            'career_name': 'Blockchain Engineer & Fintech Specialist',
            'career_description': 'Blockchain Engineers design cryptographically secure smart contracts, decentralized applications (dApps), and digital financial transaction ledgers.',
            'primary_keywords': ['Computer Science', 'Software Engineering', 'Mathematics', 'Finance'],
            'secondary_keywords': ['Statistics', 'Economics'],
            'explanations': {
                'Computer Science': 'Provides cryptography, consensus algorithms, and distributed database engineering foundations.',
                'Mathematics': 'Covers number theory and cryptographic security.'
            }
        }
    },
    {
        'keywords': ['game design', 'game develop', 'virtual reality', 'game engine', 'augmented reality', 'video game', 'video games', 'vr worlds', '3d virtual reality'],
        'priority': 85,
        'data': {
            'career_name': 'Video Game Developer & VR Specialist',
            'career_description': 'Game Developers and VR Specialists program 3D interactive game physics, design immersive virtual reality worlds, and script gameplay mechanics.',
            'primary_keywords': ['Computer Science', 'Software Engineering', 'Information Technology', 'Industrial Art'],
            'secondary_keywords': ['Mathematics', 'Physics', 'Theatre Arts'],
            'explanations': {
                'Computer Science': 'Core programming degree for 3D computer graphics, physics simulation, and game engines.',
                'Software Engineering': 'Complex interactive software architecture and engine optimization.'
            }
        }
    },
    {
        'keywords': ['cloud engineer', 'cloud architect', 'devops', 'aws', 'azure', 'docker', 'kubernetes', 'cloud comput', 'cloud infrastructure', 'cloud clusters'],
        'priority': 85,
        'data': {
            'career_name': 'Cloud Solutions Architect & DevOps Engineer',
            'career_description': 'Cloud and DevOps Engineers design elastic cloud server infrastructure, automate continuous deployment pipelines, and maintain high-availability web services.',
            'primary_keywords': ['Computer Science', 'Information Technology', 'Computer Engineering', 'Telecommunication Engineering'],
            'secondary_keywords': ['Mathematics', 'Physics'],
            'explanations': {
                'Computer Science': 'Direct computing degree covering distributed systems, network architecture, and cloud virtualization.',
                'Information Technology': 'Enterprise server management and system administration.'
            }
        }
    },
    {
        'keywords': ['cyber', 'network security', 'information security', 'malware', 'firewall', 'firewalls', 'penetration test', 'vulnerabilit'],
        'regex_patterns': [r'\bhack(er|ing)?\b'],
        'priority': 85,
        'data': {
            'career_name': 'Cybersecurity Analyst / Network Engineer',
            'career_description': 'Cybersecurity Analysts protect networks, cloud systems, and data infrastructure against cyber threats, security breaches, and unauthorized intrusion.',
            'primary_keywords': ['Computer Science', 'Information Technology', 'Telecommunication Engineering', 'Computer Engineering'],
            'secondary_keywords': ['Mathematics', 'Physics', 'Computing'],
            'explanations': {
                'Computer Science': 'Core degree providing programming, network architecture, and cryptography algorithms.',
                'Information Technology': 'Covers systems administration, network security, and enterprise database infrastructure.',
                'Telecommunication Engineering': 'Focuses on network hardware, data communications, and signal transmission security.'
            }
        }
    },
    {
        'keywords': ['statistic', 'data analyst', 'data science', 'big data', 'machine learning', 'artificial intelligence', 'data min', 'neural network', 'predictive model', 'deep learning', 'business intelligence', 'market intelligence', 'regression metrics', 'business statistics'],
        'priority': 80,
        'data': {
            'career_name': 'Data Scientist & Statistical Analyst',
            'career_description': 'Data Scientists and Statisticians analyze big data repositories, design machine learning algorithms, and derive predictive insights for industry and governance.',
            'primary_keywords': ['Statistics', 'Computer Science', 'Mathematics', 'Information Technology'],
            'secondary_keywords': ['Economics', 'Business Administration'],
            'explanations': {
                'Statistics': 'Direct degree in statistical inference, regression, and data modeling.',
                'Computer Science': 'Covers algorithm design, machine learning pipelines, and database architecture.'
            }
        }
    },
    {
        'keywords': ['robot', 'robotics', 'automation', 'mechatronics', 'automated machine', 'autonomous robot', 'robotic arm', 'factory production lines', 'motherboard', 'computer chip', 'microprocessor'],
        'priority': 80,
        'data': {
            'career_name': 'Robotics & Automation Engineer',
            'career_description': 'Robotics and Automation Engineers design, program, and build robotic devices, autonomous systems, and industrial automated machinery.',
            'primary_keywords': ['Mechanical Engineering', 'Electrical/Electronic Engineering', 'Computer Engineering', 'Biomedical Engineering'],
            'secondary_keywords': ['Physics', 'Mathematics', 'Computer Science'],
            'explanations': {
                'Mechanical Engineering': 'Provides mechanical design, kinematics, and dynamic systems engineering foundations.',
                'Electrical/Electronic Engineering': 'Covers microcontrollers, sensors, power electronics, and robotic motor control.',
                'Computer Engineering': 'Bridges hardware and software for embedded system robotics programming.'
            }
        }
    },
    {
        'keywords': ['telecom', 'fiber optic', '5g', 'wireless signal', 'satellite commun', 'cellular network', 'signal tower', 'signal towers'],
        'priority': 80,
        'data': {
            'career_name': 'Telecommunications & Network Engineer',
            'career_description': 'Telecommunication Engineers design wireless cellular networks, fiber-optic transmission backbones, and satellite communication infrastructure.',
            'primary_keywords': ['Telecommunication Engineering', 'Electrical/Electronic Engineering', 'Computer Engineering'],
            'secondary_keywords': ['Physics', 'Mathematics'],
            'explanations': {
                'Telecommunication Engineering': 'Direct engineering path for wireless signals, radio frequency, and network infrastructure.',
                'Electrical/Electronic Engineering': 'Provides circuit electronics and electromagnetics fundamentals.'
            }
        }
    },
    {
        'keywords': ['software', 'developer', 'coder', 'programmer', 'web app', 'mobile app', 'fullstack', 'frontend', 'backend', 'coding', 'algorithms', 'mathematical coding', 'sql database', 'enterprise it', 'local area network', 'it servers', 'application developer'],
        'regex_patterns': [r'\bapps?\b'],
        'priority': 70,
        'data': {
            'career_name': 'Software Engineer / Application Developer',
            'career_description': 'Software Engineers design, build, and deploy computer applications, web systems, and mobile software.',
            'primary_keywords': ['Computer Science', 'Software Engineering', 'Information Technology', 'Computer Engineering'],
            'secondary_keywords': ['Mathematics', 'Engineering', 'Electrical'],
            'explanations': {
                'Computer Science': 'Core degree program covering algorithms, programming languages, and software architecture.',
                'Software Engineering': 'Specialized engineering path focused on application development and software systems.',
                'Information Technology': 'Applied computing degree covering web, networking, and software systems.'
            }
        }
    },

    # --- 3. Built Environment & Engineering ---
    {
        'keywords': ['quantity survey', 'cost estimator', 'construction cost', 'building budget', 'bill of quantities', 'bills of quantities', 'construction budget', 'building cost', 'audit building material', 'multimillion dollar construction'],
        'priority': 85,
        'data': {
            'career_name': 'Quantity Surveyor & Construction Cost Estimator',
            'career_description': 'Quantity Surveyors manage construction project finances, prepare bills of quantities, control building contracts, and audit structural material budgets.',
            'primary_keywords': ['Quantity Surveying', 'Construction Technology', 'Civil Engineering', 'Building Technology'],
            'secondary_keywords': ['Mathematics', 'Physics', 'Economics'],
            'explanations': {
                'Quantity Surveying': 'Direct degree covering construction contract economics and cost management.',
                'Construction Technology': 'Provides structural and site building management foundations.'
            }
        }
    },
    {
        'keywords': ['real estate', 'property value', 'property valuer', 'estate manage', 'land economy', 'property develop', 'landlord', 'property portfolio', 'commercial shopping mall', 'residential estate', 'property investment'],
        'priority': 80,
        'data': {
            'career_name': 'Real Estate & Land Economy Specialist',
            'career_description': 'Real Estate and Land Economy specialists value commercial properties, manage property portfolios, structure land acquisitions, and oversee urban real estate development.',
            'primary_keywords': ['Land Economy', 'Real Estate', 'Business Administration', 'Architecture'],
            'secondary_keywords': ['Economics', 'Finance', 'Geography'],
            'explanations': {
                'Land Economy': 'Direct degree covering land valuation, property law, and real estate finance.',
                'Real Estate': 'Direct specialized program in property asset management.'
            }
        }
    },
    {
        'keywords': ['geomatic', 'land survey', 'surveyor', 'cartograph', 'mapping', 'spatial survey', 'cadastral', 'boundary beacon', 'demarcate land'],
        'regex_patterns': [r'\bgis\b'],
        'priority': 80,
        'data': {
            'career_name': 'Geomatic & Spatial Survey Engineer',
            'career_description': 'Geomatic Engineers and Surveyors map geographic terrain, deploy satellite GPS/GIS data systems, and establish precise land boundary measurements for construction.',
            'primary_keywords': ['Geomatic', 'Civil Engineering', 'Land Economy', 'Architecture'],
            'secondary_keywords': ['Mathematics', 'Physics', 'Geography'],
            'explanations': {
                'Geomatic': 'Direct engineering degree for land surveying, geodesy, and GIS mapping.',
                'Civil Engineering': 'Provides infrastructure and site construction survey foundations.'
            }
        }
    },
    {
        'keywords': ['architect', 'architecture', 'landscape design', 'urban planning', 'smart cities', 'skyscraper', 'design building', 'design house', 'building design', 'urban design', 'botanical garden', 'landscape architecture', 'zero-carbon', 'city zoning'],
        'priority': 75,
        'data': {
            'career_name': 'Architect / Urban Planner',
            'career_description': 'Architects and Urban Planners design functional buildings, residential structures, sustainable landscapes, and modern urban infrastructure.',
            'primary_keywords': ['Architecture', 'Landscape Design', 'Settlement Planning', 'Building Technology'],
            'secondary_keywords': ['Civil Engineering', 'Physics', 'Mathematics', 'Art'],
            'explanations': {
                'Architecture': 'Direct professional degree covering spatial design, structural aesthetics, and architectural drafting.',
                'Landscape Design': 'Specialized path for exterior spaces, environmental design, and urban landscape ecology.',
                'Settlement Planning': 'Focuses on regional infrastructure, urban growth management, and municipal planning.'
            }
        }
    },
    {
        'keywords': ['pilot', 'aviation', 'aero', 'airplane', 'airplanes', 'aeroplane', 'aeroplanes', 'aircraft', 'aircrafts', 'flight', 'plane', 'planes', 'aerospace', 'rocket', 'satellite orbit', 'fly commercial'],
        'priority': 80,
        'data': {
            'career_name': 'Aerospace / Aeronautical Engineer',
            'career_description': 'Aerospace and Aeronautical Engineers design, test, build, and maintain aircraft, spacecraft, avionics systems, and flight hardware.',
            'primary_keywords': ['Aerospace', 'Aeronautical', 'Mechanical Engineering'],
            'secondary_keywords': ['Physics', 'Electrical', 'Mathematics'],
            'explanations': {
                'Aerospace': 'Direct engineering path for aircraft and propulsion system design.',
                'Aeronautical': 'Specialized engineering field focused on flight and aircraft design.',
                'Mechanical Engineering': 'Provides mechanical design and aerodynamics fundamentals.'
            }
        }
    },
    {
        'keywords': ['geolog', 'rock strata', 'mineral', 'mining engineer', 'gold mine', 'earthquake', 'geophysic', 'subterranean ore', 'rock blasting'],
        'regex_patterns': [r'\brocks?\b'],
        'priority': 80,
        'data': {
            'career_name': 'Geological & Mining Engineer',
            'career_description': 'Geologists and Mining Engineers explore subterranean mineral deposits, design surface and underground mines, analyze seismic activity, and manage mineral extraction.',
            'primary_keywords': ['Geological Engineering', 'Mining Engineering', 'Materials Engineering', 'Civil Engineering'],
            'secondary_keywords': ['Physics', 'Chemistry', 'Mathematics'],
            'explanations': {
                'Geological Engineering': 'Direct engineering degree for mineral exploration, geophysics, and rock mechanics.',
                'Mining Engineering': 'Direct engineering path for ore extraction, mine safety, and blasting.'
            }
        }
    },
    {
        'keywords': ['chemical engineer', 'petrochem', 'oil and gas', 'refinery', 'petroleum', 'crude oil', 'drilling rig', 'chemical synthesis'],
        'priority': 80,
        'data': {
            'career_name': 'Chemical & Petroleum Engineer',
            'career_description': 'Chemical and Petroleum Engineers design industrial chemical plants, manage oil and gas extraction, and synthesize fuels, polymers, and pharmaceuticals.',
            'primary_keywords': ['Chemical Engineering', 'Petroleum Engineering', 'Petrochemical', 'Materials Engineering'],
            'secondary_keywords': ['Chemistry', 'Physics', 'Mathematics'],
            'explanations': {
                'Chemical Engineering': 'Direct engineering degree for chemical plant design and industrial synthesis.',
                'Petroleum Engineering': 'Specialized engineering path for oil and gas reservoir extraction.',
                'Materials Engineering': 'Covers polymer science and material properties.'
            }
        }
    },
    {
        'keywords': ['metallurg', 'materials engineer', 'alloys', 'smelting', 'nanomaterial', 'composite material', 'metal alloy', 'metal alloys'],
        'priority': 80,
        'data': {
            'career_name': 'Materials & Metallurgical Engineer',
            'career_description': 'Materials and Metallurgical Engineers develop advanced metal alloys, composite polymers, ceramics, and nanomaterials for manufacturing and aerospace.',
            'primary_keywords': ['Materials Engineering', 'Mechanical Engineering', 'Chemical Engineering'],
            'secondary_keywords': ['Physics', 'Chemistry', 'Mathematics'],
            'explanations': {
                'Materials Engineering': 'Direct engineering degree for metallurgy, crystal structures, and composite material synthesis.',
                'Mechanical Engineering': 'Covers solid mechanics and stress analysis.'
            }
        }
    },
    {
        'keywords': ['solar', 'solar energy', 'renewable energy', 'electric', 'electrical', 'power grid', 'wind turbine', 'clean energy', 'high-voltage', 'transformer', 'wind power'],
        'priority': 75,
        'data': {
            'career_name': 'Electrical & Renewable Energy Engineer',
            'career_description': 'Electrical and Renewable Energy Engineers design power generation facilities, solar energy systems, national electric grids, and electronic devices.',
            'primary_keywords': ['Electrical/Electronic Engineering', 'Renewable Energy', 'Energy Systems', 'Physics'],
            'secondary_keywords': ['Mathematics', 'Mechanical Engineering'],
            'explanations': {
                'Electrical/Electronic Engineering': 'Direct engineering degree covering power systems, circuit design, and electromagnetics.',
                'Renewable Energy': 'Specialized path focused on solar, wind, biomass, and sustainable power grids.',
                'Physics': 'Provides deep theoretical electromagnetic and quantum foundations.'
            }
        }
    },
    {
        'keywords': ['water supply dam', 'potable water', 'water treatment plant', 'municipal water supply'],
        'priority': 85,
        'data': {
            'career_name': 'Healthcare & Allied Health Practitioner',
            'career_description': 'Water and Public Health specialists design municipal water purification infrastructure, manage public reservoir dams, and safeguard potable water quality.',
            'primary_keywords': ['Water and Public Health Engineering', 'Civil Engineering', 'Public Health'],
            'secondary_keywords': ['Chemistry', 'Physics'],
            'explanations': {
                'Water and Public Health Engineering': 'Direct engineering degree for potable water supply, environmental health, and municipal sanitation.',
                'Civil Engineering': 'Provides structural and hydraulic infrastructure engineering foundations.'
            }
        }
    },
    {
        'keywords': ['bridge', 'structural', 'construction engineer', 'roads', 'concrete flyover', 'highway', 'dam', 'concrete pour', 'construction work', 'building site', 'highways'],
        'conditional_keywords': {
            'infrastructure': {'exclude': ['cloud', 'network', 'it infrastructure']},
            'civil': {'exclude': ['civil rights', 'civil law', 'civil case', 'civil liberties']}
        },
        'priority': 70,
        'data': {
            'career_name': 'Civil & Structural Engineer',
            'career_description': 'Civil and Structural Engineers plan, design, and oversee construction of essential infrastructure including roads, bridges, water supply systems, and tall buildings.',
            'primary_keywords': ['Civil Engineering', 'Geomatic', 'Construction Technology'],
            'secondary_keywords': ['Physics', 'Mathematics', 'Engineering'],
            'explanations': {
                'Civil Engineering': 'Direct engineering degree for infrastructure, structural design, and urban works.',
                'Geomatic': 'Specialized survey engineering for land spatial analysis and construction.',
                'Construction Technology': 'Provides management and construction science foundations.'
            }
        }
    },
    {
        'keywords': ['vehicle engine', 'mechanical system', 'mechanical systems', 'mechanical design'],
        'priority': 75,
        'data': {
            'career_name': 'Mechanical & Automotive Engineer',
            'career_description': 'Mechanical Engineers design thermal systems, automotive powertrains, manufacturing machinery, and fluid power equipment.',
            'primary_keywords': ['Mechanical Engineering', 'Materials Engineering', 'Electrical/Electronic Engineering'],
            'secondary_keywords': ['Physics', 'Mathematics'],
            'explanations': {
                'Mechanical Engineering': 'Direct engineering degree for mechanical design, thermodynamics, and fluid dynamics.'
            }
        }
    },

    # --- 4. Agriculture, Marine, Forestry & Environment ---
    {
        'keywords': ['marine', 'ocean', 'sea life', 'fisheries', 'aquaculture', 'water life', 'fish farming', 'fish farm', 'fish species', 'marine ecosystem', 'marine biology', 'tilapia', 'catfish', 'marine vessel', 'container ship'],
        'priority': 80,
        'data': {
            'career_name': 'Marine Scientist / Fisheries Biologist',
            'career_description': 'Marine Scientists and Fisheries Biologists study marine ecosystems, ocean life conservation, sustainable fish farming, and coastal aquatic environments.',
            'primary_keywords': ['Fisheries', 'Aquaculture', 'Marine', 'Oceanography', 'Biological Science'],
            'secondary_keywords': ['Biology', 'Chemistry', 'General Science'],
            'explanations': {
                'Fisheries': 'Direct degree covering fish health, breeding, aquaculture technology, and water ecosystem management.',
                'Aquaculture': 'Applied breeding and sustainable aquatic production systems.',
                'Biological Science': 'Provides strong biological and ecological science foundations.'
            }
        }
    },
    {
        'keywords': ['forest', 'forestry', 'wildlife', 'natural resources', 'conservation', 'biodiversity', 'ecology', 'national park', 'tree conservation', 'rainforest', 'illegal logging', 'endangered elephant', 'polluted river', 'wetland', 'plant trees', 'canopy walkway', 'nature park', 'plastic waste'],
        'priority': 75,
        'data': {
            'career_name': 'Environmental & Wildlife Conservationist',
            'career_description': 'Conservationists and Forestry experts manage wildlife habitats, protect national park biodiversity, control forest resources, and combat environmental degradation.',
            'primary_keywords': ['Forest Resources', 'Natural Resources', 'Environmental Science', 'Wildlife', 'Ecotourism'],
            'secondary_keywords': ['Biology', 'Chemistry', 'Agriculture'],
            'explanations': {
                'Forest Resources': 'Direct degree managing sustainable forestry, timber conservation, and biodiversity.',
                'Natural Resources': 'Comprehensive stewardship of soil, water, forest, and mineral ecosystems.',
                'Environmental Science': 'Covers pollution control, ecological monitoring, and environmental impact assessment.'
            }
        }
    },
    {
        'keywords': ['food science', 'food process', 'food safet', 'food quality', 'beverage', 'brewing', 'food preservation', 'food shelf life', 'canned food', 'post harvest', 'grain silo', 'juice beverage', 'drying system'],
        'priority': 80,
        'data': {
            'career_name': 'Food Scientist & Quality Assurance Specialist',
            'career_description': 'Food Scientists formulate nutritious consumer foods, design industrial food preservation methods, and enforce international hygiene and quality standards.',
            'primary_keywords': ['Food Science and Technology', 'Dietetics', 'Biochemistry', 'Agriculture', 'Post Harvest'],
            'secondary_keywords': ['Chemistry', 'Biology'],
            'explanations': {
                'Food Science and Technology': 'Direct degree program covering food biochemistry, processing machinery, and sensory quality.',
                'Biochemistry': 'Covers nutritional biochemical analysis.',
                'Post Harvest': 'Focuses on post-harvest preservation and loss prevention.'
            }
        }
    },
    {
        'keywords': ['meteorolog', 'weather forecast', 'climate change', 'hurricane', 'atmosphere', 'rainfall', 'atmospheric pressure', 'weather prediction', 'monsoon'],
        'priority': 80,
        'data': {
            'career_name': 'Meteorologist & Climate Scientist',
            'career_description': 'Meteorologists and Climate Scientists analyze atmospheric thermodynamics, satellite radar data, and climate models to forecast weather and track climate patterns.',
            'primary_keywords': ['Meteorology', 'Physics', 'Mathematics', 'Environmental Science'],
            'secondary_keywords': ['Geography', 'Computer Science'],
            'explanations': {
                'Meteorology': 'Direct degree covering atmospheric physics, climatology, and weather forecasting.',
                'Physics': 'Provides fluid dynamics and atmospheric thermodynamics foundations.'
            }
        }
    },
    {
        'keywords': ['plant crop', 'crop yield', 'farm', 'farming', 'agriculture', 'agronomy', 'soil', 'agric', 'horticulture', 'commercial farm', 'crop disease', 'cocoa', 'maize', 'cattle ranch', 'poultry hatchery', 'greenhouse', 'fertilizer', 'agribusiness', 'grain storage', 'dairy farming', 'animal husbandry', 'exotic flowers'],
        'priority': 70,
        'data': {
            'career_name': 'Agricultural Scientist / Agronomist',
            'career_description': 'Agricultural Scientists and Agronomists improve crop yields, manage livestock health, innovate sustainable farming techniques, and safeguard food security.',
            'primary_keywords': ['Agriculture', 'Agricultural', 'Agribusiness', 'Post Harvest', 'Animal Science'],
            'secondary_keywords': ['Biology', 'Chemistry', 'General Science'],
            'explanations': {
                'Agriculture': 'Comprehensive degree covering crop science, soil fertility, and agricultural systems.',
                'Agricultural': 'Applied agricultural technology and production sciences.',
                'Agribusiness': 'Combines agricultural knowledge with business management and economics.',
                'Animal Science': 'Covers livestock breeding, dairy production, and animal husbandry.'
            }
        }
    },

    # --- 5. Business, Finance & Law ---
    {
        'keywords': ['actuar', 'insurance risk', 'pension fund', 'financial risk model', 'mortality table', 'underwrite commercial insurance', 'life insurance', 'pension'],
        'priority': 85,
        'data': {
            'career_name': 'Actuary & Financial Risk Analyst',
            'career_description': 'Actuaries apply mathematical probability, statistical modeling, and economic theory to evaluate long-term financial risks in insurance, pensions, and investments.',
            'primary_keywords': ['Actuarial Science', 'Mathematics', 'Statistics', 'Finance', 'Business Administration'],
            'secondary_keywords': ['Economics', 'Computer Science'],
            'explanations': {
                'Actuarial Science': 'Direct degree preparing accredited actuaries in risk modeling and life contingencies.',
                'Mathematics': 'Provides advanced calculus, stochastic processes, and probability theory.'
            }
        }
    },
    {
        'keywords': ['account', 'accounting', 'accountant', 'auditor', 'audit', 'balance sheet', 'financial statement', 'tax returns', 'financial auditor', 'commercial banking', 'capital market', 'stock exchange', 'securities and capital', 'financial portfolio'],
        'priority': 75,
        'data': {
            'career_name': 'Accountant / Financial Auditor',
            'career_description': 'Accountants and Financial Auditors manage financial records, prepare balance sheets, perform audit verifications, and analyze business financial performance.',
            'primary_keywords': ['Accounting', 'Business Administration', 'Finance'],
            'secondary_keywords': ['Economics', 'Management', 'Business'],
            'explanations': {
                'Accounting': 'Direct degree program preparing students for chartered accounting and financial management.',
                'Business Administration': 'Provides broad business, management, and financial education.',
                'Finance': 'Focuses on financial markets, corporate finance, and investment analysis.'
            }
        }
    },
    {
        'keywords': ['economist', 'macroeconomic', 'inflation', 'fiscal policy', 'monetary policy', 'gdp', 'interest rate', 'economic growth', 'foreign exchange currency', 'export economic', 'international trade'],
        'priority': 80,
        'data': {
            'career_name': 'Economist & Financial Policy Analyst',
            'career_description': 'Economists analyze macroeconomic data, track inflation trends, formulate fiscal and monetary policies, and forecast economic development.',
            'primary_keywords': ['Economics', 'Business Administration', 'Mathematics', 'Statistics'],
            'secondary_keywords': ['Political Science', 'History'],
            'explanations': {
                'Economics': 'Direct degree covering microeconomics, macroeconomics, econometrics, and development policy.',
                'Mathematics': 'Provides quantitative econometrics modeling foundations.'
            }
        }
    },
    {
        'keywords': ['human resource', 'recruiting', 'talent manage', 'employee relation', 'hr manage', 'staff training', 'workforce recruitment'],
        'priority': 80,
        'data': {
            'career_name': 'Human Resource Manager',
            'career_description': 'Human Resource Managers oversee employee recruitment, corporate talent development, compensation policies, labor relations, and organizational culture.',
            'primary_keywords': ['Business Administration', 'Psychology', 'Sociology', 'Communication Studies'],
            'secondary_keywords': ['Management', 'Economics'],
            'explanations': {
                'Business Administration': 'Direct degree track specializing in human resource management and organizational behavior.',
                'Psychology': 'Provides behavioral science and workplace psychology insights.'
            }
        }
    },
    {
        'keywords': ['supply chain', 'logistics', 'procurement', 'warehouse manage', 'freight', 'shipping', 'cargo logistics', 'freight transport', 'freight cargo', 'supply chain vendors'],
        'priority': 80,
        'data': {
            'career_name': 'Supply Chain & Logistics Specialist',
            'career_description': 'Supply Chain and Logistics Specialists coordinate global freight shipping, optimize warehouse inventory systems, and negotiate enterprise procurement contracts.',
            'primary_keywords': ['Business Administration', 'Economics', 'Agribusiness'],
            'secondary_keywords': ['Accounting', 'Mathematics'],
            'explanations': {
                'Business Administration': 'Direct degree option in logistics, supply chain operations, and procurement management.',
                'Agribusiness': 'Covers agricultural supply chains and commodity distribution.'
            }
        }
    },
    {
        'keywords': ['marketing', 'advertis', 'brand manage', 'digital marketing', 'consumer research', 'public relation', 'ad campaign', 'press conference', 'executive branding', 'advertising campaign'],
        'priority': 75,
        'data': {
            'career_name': 'Marketing & Public Relations Strategist',
            'career_description': 'Marketing and Public Relations Strategists design promotional campaigns, analyze consumer buying behaviors, manage brand identity, and drive revenue growth.',
            'primary_keywords': ['Business Administration', 'Communication Studies', 'Journalism'],
            'secondary_keywords': ['Economics', 'Psychology', 'English'],
            'explanations': {
                'Business Administration': 'Direct degree track specializing in marketing management, branding, and sales strategy.',
                'Communication Studies': 'Public relations, corporate communications, and digital media advertising.'
            }
        }
    },
    {
        'keywords': ['hotel', 'hospitality', 'tourism', 'events management', 'resort', 'luxury hotel', 'tourist destination', 'travel agency', 'culinary guest', 'guest accommodations', 'festivals and tourism', 'convention and event'],
        'priority': 75,
        'data': {
            'career_name': 'Hospitality & Tourism Manager',
            'career_description': 'Hospitality and Tourism Managers oversee international hotel operations, resort destinations, event planning, and guest experience logistics.',
            'primary_keywords': ['Hospitality', 'Tourism', 'Hospitality and Tourism', 'Business Administration', 'Marketing', 'Management', 'Ecotourism'],
            'secondary_keywords': ['Economics', 'Languages', 'French'],
            'explanations': {
                'Hospitality': 'Direct degree covering hotel management, food service operations, and customer experience.',
                'Tourism': 'Specialized program in ecotourism, travel agency operations, and destination management.',
                'Business Administration': 'Provides strategic management, finance, and marketing foundations.'
            }
        }
    },
    {
        'keywords': ['translat', 'interpret', 'linguist', 'multilingual', 'foreign language', 'french speak', 'french interpretation', 'translation'],
        'priority': 82,
        'data': {
            'career_name': 'Linguist & Professional Translator',
            'career_description': 'Linguists and Translators translate diplomatic and technical texts between international languages, provide live conference interpretation, and study language evolution.',
            'primary_keywords': ['French', 'English', 'Linguistics', 'Communication Studies', 'Ghanaian Language'],
            'secondary_keywords': ['History', 'Political Science'],
            'explanations': {
                'French': 'Direct degree covering advanced French literature, grammar, and international translation.',
                'English': 'Advanced linguistic and textual analysis.',
                'Ghanaian Language': 'Cultural linguistics and national language translation.'
            }
        }
    },
    {
        'keywords': ['diplomat', 'foreign embassy', 'embassies', 'international relations', 'peace treaty', 'ambassador', 'foreign mission'],
        'priority': 80,
        'data': {
            'career_name': 'Diplomat / International Relations Specialist',
            'career_description': 'Diplomats and International Relations Specialists represent national interests abroad, negotiate bilateral treaties, and foster global cooperation.',
            'primary_keywords': ['Political Science', 'Law', 'History', 'French'],
            'secondary_keywords': ['Sociology', 'English'],
            'explanations': {
                'Political Science': 'Direct academic pathway covering international relations, diplomacy, and global governance.',
                'Law': 'Covers international public law, treaty interpretation, and human rights.',
                'French': 'Essential diplomatic language for international organizations and African diplomacy.'
            }
        }
    },
    {
        'keywords': ['lawyer', 'attorney', 'legal practice', 'litigation', 'courtroom', 'llb', 'barrister', 'constitutional jurisprudence', 'judge', 'defend civil rights', 'justice as a lawyer', 'legal contract'],
        'regex_patterns': [r'\blaws?\b'],
        'priority': 82,
        'data': {
            'career_name': 'Lawyer / Legal Practitioner',
            'career_description': 'Lawyers advise clients on legal rights, draft legal contracts, and represent parties in courts of law.',
            'primary_keywords': ['Law', 'LLB', 'Legal'],
            'secondary_keywords': ['Political Science', 'Sociology', 'History'],
            'explanations': {
                'Law': 'Direct Bachelor of Laws (LLB) degree program required for legal education.',
                'LLB': 'Professional law degree track.'
            }
        }
    },

    # --- 6. Arts, Media, Social Sciences & Education ---
    {
        'keywords': ['music produc', 'sound engineer', 'audio record', 'beat mak', 'studio master', 'soundtrack', 'musician', 'singing', 'music composer', 'mixing audio', 'record vocal', 'vocal artists', 'sound studio', 'music tracks'],
        'priority': 82,
        'data': {
            'career_name': 'Music Producer & Audio Engineer',
            'career_description': 'Music Producers and Audio Engineers compose instrumental tracks, record vocal arrangements, mix multi-track audio, and master sound for commercial release.',
            'primary_keywords': ['Theatre Arts', 'Communication Studies', 'Computer Science'],
            'secondary_keywords': ['Physics', 'Industrial Art'],
            'explanations': {
                'Theatre Arts': 'Direct creative degree covering musicology, stage acoustics, and audio-dramatic production.',
                'Communication Studies': 'Broadcast audio engineering and sound design for media.'
            }
        }
    },
    {
        'keywords': ['journalism', 'journalist', 'reporter', 'media', 'broadcasting', 'broadcast', 'news', 'communication', 'writer', 'television', 'investigative journalism'],
        'conditional_keywords': {
            'radio': {'exclude': ['radiograph', 'radiolog']}
        },
        'priority': 70,
        'data': {
            'career_name': 'Journalist / Media & Communications Specialist',
            'career_description': 'Journalists and Media Specialists research stories, write news articles, produce broadcast programs, and communicate critical information across digital, television, radio, and print platforms.',
            'primary_keywords': ['Communication Studies', 'Journalism', 'Media', 'English', 'Public Relations'],
            'secondary_keywords': ['Political Science', 'Sociology', 'History', 'Theatre Arts', 'Information Studies'],
            'explanations': {
                'Communication Studies': 'Direct degree pathway covering news broadcasting, media writing, and public communication.',
                'Journalism': 'Direct degree track specializing in news reporting, photojournalism, and investigative media.',
                'English': 'Builds advanced writing, grammar, and literary communication fundamentals essential for journalism.'
            }
        }
    },
    {
        'keywords': ['film', 'movie', 'theatre', 'acting', 'drama', '3d animation', 'visual fx', 'visual effect', 'cgi art', 'creative arts', 'digital artist', 'direct stage plays'],
        'priority': 70,
        'data': {
            'career_name': 'Creative Media Producer / Digital Artist',
            'career_description': 'Creative Media Producers and Artists produce motion pictures, theatre productions, digital visual effects, 3D animations, and audio compositions.',
            'primary_keywords': ['Theatre Arts', 'Communication Studies', 'Computer Science', 'Industrial Art', 'Media'],
            'secondary_keywords': ['English', 'Information Studies'],
            'explanations': {
                'Theatre Arts': 'Direct creative degree covering acting, stagecraft, film directing, and dramatic production.',
                'Communication Studies': 'Broadcast media, audio-visual production, and digital storytelling.',
                'Computer Science': 'Interactive digital graphics, game engine programming, and computer animation.'
            }
        }
    },
    {
        'keywords': ['fashion', 'textile design', 'garment', 'clothing', 'apparel', 'tailor', 'sewing', 'couture', 'bespoke clothing'],
        'priority': 80,
        'data': {
            'career_name': 'Fashion Designer & Textile Artist',
            'career_description': 'Fashion Designers create haute couture apparel, design bespoke textile patterns, draft garment patterns, and manage clothing production lines.',
            'primary_keywords': ['Fashion Design', 'Textile Design', 'Intergrated Rural Art', 'Clothing and Textiles', 'Art and Design'],
            'secondary_keywords': ['Visual Arts', 'Business Administration'],
            'explanations': {
                'Fashion Design': 'Direct degree pathway covering bespoke garment styling, haute couture, and apparel technology.',
                'Textile Design': 'Specialized program covering fabric production, surface printing, and textile material sciences.',
                'Intergrated Rural Art': 'Covers indigenous textile crafts, surface design, and creative art entrepreneurship.'
            }
        }
    },
    {
        'keywords': ['archaeolog', 'artifact', 'ancient civilization', 'heritage', 'museum curator', 'excavat', 'cultural museum'],
        'priority': 80,
        'data': {
            'career_name': 'Archaeologist & Cultural Heritage Curator',
            'career_description': 'Archaeologists and Museum Curators excavate ancient historical artifacts, preserve cultural heritage sites, and curate museum exhibitions.',
            'primary_keywords': ['History', 'Archaeology', 'Heritage Studies', 'Integrated Rural Art'],
            'secondary_keywords': ['Sociology', 'Geography'],
            'explanations': {
                'History': 'Direct degree pathway covering African historiography, ancient civilizations, and archaeological theory.',
                'Integrated Rural Art': 'Preservation of indigenous material culture and artifact conservation.'
            }
        }
    },
    {
        'keywords': ['social work', 'child welfare', 'orphanage', 'social welfare', 'vulnerable', 'community outreac', 'vulnerable orphan'],
        'priority': 75,
        'data': {
            'career_name': 'Social Worker & Community Development Officer',
            'career_description': 'Social Workers advocate for vulnerable children and families, direct social welfare programs, resolve domestic crises, and empower underprivileged communities.',
            'primary_keywords': ['Social Work', 'Sociology', 'Political Science', 'Psychology'],
            'secondary_keywords': ['History', 'Education'],
            'explanations': {
                'Social Work': 'Direct professional degree in community case work, child protection, and social policy.',
                'Sociology': 'Provides systemic insights into social structures and societal inequality.'
            }
        }
    },
    {
        'keywords': ['teach', 'teacher', 'teaching', 'education', 'lecturer', 'tutor', 'special education', 'deaf', 'blind', 'special needs', 'classroom educator', 'mathematics and physics as a professional teacher'],
        'priority': 60,
        'data': {
            'career_name': 'Professional Educator / Teacher',
            'career_description': 'Professional Educators deliver instruction, inspire students in specialized subjects, design curricula, and foster academic development.',
            'primary_keywords': ['Education', 'B.Ed.', 'Teacher', 'Special Education'],
            'secondary_keywords': ['Arts', 'Science', 'Mathematics', 'English'],
            'explanations': {
                'Education': 'Direct Bachelor of Education degree equipping teachers with pedagogy and subject mastery.',
                'B.Ed.': 'Official teaching qualification in Ghana.',
                'Special Education': 'Specialized training for teaching students with diverse learning abilities.'
            }
        }
    },
    {
        'keywords': ['sport', 'sports', 'athlete', 'athletic', 'fitness', 'football coach', 'coach', 'exercise', 'biomechanic', 'rehabilitate injured football'],
        'priority': 65,
        'data': {
            'career_name': 'Sports Scientist / Athletic Performance Coach',
            'career_description': 'Sports Scientists and Performance Coaches optimize athlete endurance, manage sports rehabilitation, study biomechanics, and promote physical fitness.',
            'primary_keywords': ['Sports Science', 'Physiotherapy and Sports Science', 'Physical Education', 'Human Biology'],
            'secondary_keywords': ['Biology', 'Health'],
            'explanations': {
                'Sports Science': 'Direct degree covering athletic biomechanics, exercise physiology, and sports nutrition.',
                'Physiotherapy and Sports Science': 'Clinical injury rehabilitation, athletic recovery, and movement science.'
            }
        }
    },
]

