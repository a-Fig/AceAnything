from typing import List, Tuple
from pathlib import Path # Added import
from quizclass import Quiz, openpdf # quizclass.py should contain openpdf
import questionclass as qc

# pypdf is used by the openpdf function in quizclass.py
# If openpdf were defined locally here, we'd need: import pypdf

# --- Source Materials ---
# Construct paths relative to this file's location
CURRENT_DIR = Path(__file__).resolve().parent

# Define PDF filenames (assuming they are directly in the 'premade_quizzes' directory with this script)
source_material_traffic_laws_pdf_name = "DL600CaliforniaHandbook.pdf"
source_material_ap_us_history_pdf_name = "AP US History Quiz Prep_.pdf" # Updated to actual filename
source_material_usa_citizens_test_pdf_name = "US Citizenship Test Knowledge Report_.pdf" # Updated to actual filename

# Construct full Path objects
source_material_traffic_laws_filename_path = CURRENT_DIR / source_material_traffic_laws_pdf_name
source_material_ap_us_history_filename_path = CURRENT_DIR / source_material_ap_us_history_pdf_name # Updated
source_material_usa_citizens_test_filename_path = CURRENT_DIR / source_material_usa_citizens_test_pdf_name # Updated

# Helper function to safely load PDF content
def _load_pdf_material(pdf_path: Path) -> str:
    if not pdf_path.is_file():
        print(f"CRITICAL ERROR: Premade quiz PDF not found at {pdf_path}. "
              f"Ensure the file is in the correct directory and committed to the repository.")
        return ""  # Return empty string if file not found
    try:
        content = openpdf(pdf_path) # openpdf from quizclass.py is expected to return text content
        if not content or not content.strip():
            print(f"WARNING: Premade quiz PDF at {pdf_path} was opened but yielded no text content.")
            return ""
        # print(f"Successfully loaded PDF: {pdf_path}") # Optional: for verbose logging during development
        return content
    except Exception as e:
        print(f"ERROR: Failed to open or process premade quiz PDF at {pdf_path}: {e}")
        return "" # Return empty string on error

# Load source materials using the helper function
source_material_traffic_laws = _load_pdf_material(source_material_traffic_laws_filename_path)
source_material_ap_us_history = _load_pdf_material(source_material_ap_us_history_filename_path) # New
source_material_usa_citizens_test = _load_pdf_material(source_material_usa_citizens_test_filename_path) # New


# --- Quiz: California Traffic Laws ---
# Ensure this section and others below correctly use the loaded source_material_traffic_laws,
# source_material_quiz1, source_material_quiz2 strings.
# If these strings are empty due to loading errors, the quiz generation based on them
# might result in empty or minimal quizzes. Consider handling empty source material
# within your Quiz class or generation logic if needed.

traffic_quiz_sections = []

# --- Category 1: Traffic Laws and Regulations ---
# Covers: Basic Speed Law, speed limits, headlight use, BAC limits, seatbelts, cell phone/headphone use, provisional license, open containers, evading police.
traffic_laws_and_regulations_questions: List[qc.Question] = [
    qc.MultipleChoice(
        question="What does California's \"Basic Speed Law\" require drivers to do?",
        correct_answers=[
            "Never drive faster than is safe for current conditions, even if below the posted limit.",
            "Never drive faster than is safe for current conditions."
            ],
        wrong_answers=[
            "Always drive at the posted speed limit, regardless of conditions.",
            "Keep up with the flow of traffic, even if it means going over the speed limit.",
            "Drive 5 mph below the speed limit at night or in bad weather.",
            "Always drive at the posted speed limit.",
            "Always match the speed of surrounding traffic."
        ],
        explanation="California's Basic Speed Law (CVC 22350) mandates that a driver must never operate their vehicle faster than is safe for the prevailing conditions, irrespective of the posted speed limit. Factors like weather (rain, fog, ice), visibility, traffic volume, road surface, and road design (curves, hills) dictate the safe speed. Driving the posted limit might be unsafe and illegal if conditions are hazardous. You can receive a speeding ticket for violating the Basic Speed Law even if driving below the posted speed limit if conditions warrant a slower speed. For example, going 65 mph on a freeway during dense fog or heavy rain could be deemed unsafe. The law requires using good judgment and adjusting speed for darkness, curves, traffic, weather, or any hazards."
    ),
    qc.MultipleChoice(
        question="What is the default speed limit in a California business or residential district unless otherwise posted?",
        correct_answers=["25 mph"],
        wrong_answers=[
            "20 mph",
            "30 mph",
            "35 mph"
        ],
        explanation="Unless a different speed limit is posted, the default (prima facie) speed limit in California business and residential districts is 25 mph. This reduced speed is necessary due to increased pedestrian activity, vehicles entering/exiting driveways and parking spots, and other potential hazards common in these areas."
    ),
    qc.MultipleChoice(
        question="When must you dim your high-beam headlights when approaching an oncoming vehicle?",
        correct_answers=["Within 500 feet"],
        wrong_answers=[
            "Within 300 feet",
            "Within 700 feet",
            "Only when they flash their lights at you"
        ],
        explanation="California law requires drivers to switch from high-beam to low-beam headlights when approaching an oncoming vehicle within 500 feet to avoid blinding the other driver. You should also use low beams when following another vehicle within 300 feet."
    ),
    qc.ShortAnswer(
        question="Under what conditions, besides darkness, are you required to use your headlights in California?",
        correct_answer=[
            "When visibility is less than 1,000 feet",
            "Poor visibility (less than 1000 ft)",
            "When windshield wipers are in continuous use due to weather (rain, snow, fog)",
            "During rain requiring wipers",
            "During snow requiring wipers",
            "During fog requiring wipers",
            "Headlights must be on when visibility is less than 1,000 feet or when windshield wipers are continuously in use."
        ],
        explanation="California Vehicle Code (CVC) 24400 mandates headlight use not only during darkness (30 minutes after sunset to 30 minutes before sunrise), but also anytime visibility is less than 1,000 feet, or whenever weather conditions like rain, snow, or fog necessitate the continuous use of windshield wipers (the \"wipers on, lights on\" rule). This ensures your vehicle is visible to others and you can see the road adequately.",
        grading_instructions="Perfect score for mentioning either the visibility constraint ('less than 1,000 feet') OR the wiper condition ('using wipers due to weather' or specific examples like rain/snow/fog). Vague answers like 'bad weather' without specifics get a lower score."
    ),
    qc.TrueFalseQuestion(
        question="True or False: In California, you must turn on your headlights 30 minutes AFTER sunset and leave them on until 30 minutes BEFORE sunrise.",
        correct_answers=["True"],
        wrong_answers=["False"],
        explanation="Correct. California Vehicle Code (CVC) 24400 defines darkness for headlight use as this period. Additionally, headlights are required when visibility is poor (less than 1,000 ft) or when windshield wipers are required due to weather."
    ),
    qc.ShortAnswer(
        question="What are the legal Blood Alcohol Concentration (BAC) limits for drivers in California? List the limits for adults (21+), minors (<21), and those on DUI probation.",
        correct_answer=[
            "For drivers 21 years or older: 0.08% or higher is illegal.",
            "For drivers under 21 years old: 0.01% or higher is illegal (Zero Tolerance).",
            "For drivers on DUI probation (any age): 0.01% or higher is illegal."
        ],
        explanation="California has specific BAC limits. For drivers 21 and over, it's illegal to drive with a BAC of 0.08% or more. Under the Zero Tolerance Law, drivers under 21 face a 0.01% limit. This same 0.01% limit applies to any driver on DUI probation. Impairment can begin below these limits.",
        grading_instructions="Full credit requires correctly stating all three distinct BAC limits (0.08% for 21+, 0.01% for <21, and 0.01% for DUI probation). Partial credit if only the adult limit (0.08%) is correct or if other limits are identified as stricter but the exact percentage is wrong."
    ),
    qc.TrueFalseQuestion(
        question="True or False: In California, a driver under 21 years old may legally drive with a BAC of 0.05%.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. California has a Zero Tolerance Law for drivers under 21. It is illegal for them to drive with a BAC of 0.01% or higher. A BAC of 0.05% would be significantly over this limit."
    ),
    qc.MultipleChoice(
        question="What is the illegal blood alcohol concentration (BAC) for a driver age 21 or older in California?",
        correct_answers=["0.08%"],
        wrong_answers=[
            "0.01%",
            "0.05%",
            "0.10%"
        ],
        explanation="For adults 21 and over, it is illegal to drive with a BAC of 0.08% or higher. This is the 'per se' limit. Even below 0.08%, you can be arrested if you show impairment. For commercial drivers, the limit is 0.04%, and for those under 21 or on DUI probation, it's 0.01% (zero tolerance)."
    ),
    qc.MultipleChoice(
        question="Who is required by California law to wear a seatbelt in a moving vehicle?",
        correct_answers=["The driver and all passengers 8 years old or older (or at least 4\'9\" tall). Younger children need appropriate child restraints."],
        wrong_answers=[
            "Only the driver and front seat passengers.",
            "Only occupants under 18 years old.",
            "Only the driver; adult passengers choose for themselves.",
            "The driver and front-seat passenger must wear seat belts; rear-seat belts are optional for adults."
        ],
        explanation="California law mandates that the driver and all passengers aged 8 years or older, or who are at least 4 feet 9 inches tall, must be secured by a safety belt. Children under 8 or shorter than 4'9\" must be in an appropriate child restraint system (car seat or booster) in the back seat. This applies to occupants in both front and back seats. The driver is responsible for ensuring passengers under 16 are properly restrained."
    ),
    qc.TrueFalseQuestion(
        question="True or False: It is legal for a driver 18 years or older to send a text message while driving in California, as long as the vehicle is stopped at a red light.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. It is illegal for drivers of any age to write, send, or read text messages or operate a handheld phone/electronic device while driving in California, even when stopped at a red light (CVC 23123.5)."
    ),
    qc.MultipleChoice(
        question="Which of these actions is illegal while driving in California regarding headphones or cell phones?",
        correct_answers=["Driving with headphones or earplugs covering both ears."],
        wrong_answers=[
            "Using your car's cruise control on a residential street.",
            "Hanging a small, non-obstructing object from the rearview mirror.",
            "Using a hands-free Bluetooth device for a phone call if you are over 18.",
            "Listening to music through a single earbud.",
            "Having music playing on your car's speakers."
        ],
        explanation="It is against California law to wear a headset or earplugs that cover both ears simultaneously while driving, as this can prevent you from hearing sirens, horns, or other important sounds. Using a single earbud or earpiece is generally permitted. Drivers over 18 may use hands-free devices for calls, but drivers under 18 may not use any phone device, even hands-free (except for emergencies)."
    ),
     qc.TrueFalseQuestion(
        question="True or False: It is legal for a driver under 18 to use a cell phone while driving as long as it is hands-free.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. California law prohibits drivers under the age of 18 from using ANY wireless communication device while driving, including cell phones, even if equipped with a hands-free feature. Exceptions exist only for emergency purposes."
    ),
    qc.MultipleChoice(
        question="For the first 12 months after getting a provisional license (driver under 18), when can they typically transport passengers under 20 years old without qualified adult supervision?",
        correct_answers=["Generally, they cannot transport passengers under 20 without supervision during the first 12 months."],
        wrong_answers=[
            "Between 5 a.m. and 11 p.m., regardless of passengers.",
            "After having the license for 6 months.",
            "If the passengers are family members (e.g., siblings).",
            "At any time, day or night, once they've held a license for 6 months."
        ],
        explanation="During the first 12 months of holding a provisional license (or until turning 18), a driver cannot transport passengers under 20 years old unless accompanied by a licensed parent/guardian, instructor, or other licensed driver 25 years of age or older. They also may not drive between 11 p.m. and 5 a.m. without such supervision. Exceptions exist for specific necessities (e.g., medical, school, employment reasons with documentation) but not for general transport of young passengers."
    ),
    qc.MultipleChoice(
        question="What does California law state about open containers of alcohol in a vehicle?",
        correct_answers=["An open alcoholic beverage container is only legal if kept in the trunk or an area not normally occupied by passengers."],
        wrong_answers=[
            "It's legal to keep an opened alcoholic drink in the glove compartment if it's locked.",
            "An open alcohol container can be in the passenger area if the driver isn't drinking it.",
            "Opened containers are allowed in the back seat as long as the driver can't reach them.",
            "It is legal to transport an unopened container of alcohol in the passenger compartment of a vehicle."
        ],
        explanation="California law prohibits driving with any open container of alcohol (any beverage with 0.5% or more alcohol by volume that has been opened, seal broken, or contents partially removed) accessible to the driver or passengers. It must be kept in the trunk. If the vehicle has no trunk, it may be kept in some other area of the vehicle not normally occupied by the driver or passengers (e.g., bed of a pickup). The glove compartment is NOT a legal place for an open container, even if locked. Unopened, factory-sealed containers can generally be transported in the passenger compartment."
    ),
    qc.MultipleChoice(
        question="A police officer with lights and siren is chasing a driver who refuses to stop. If a person is seriously injured during this chase, what are potential consequences for the evading driver?",
        correct_answers=["Imprisonment in state prison for up to 7 years (felony), in addition to fines."],
        wrong_answers=[
            "A maximum $1,000 fine and traffic school.",
            "Misdemeanor with no more than 1 year in county jail if it's a first offense.",
            "Only a ticket for evading, if no one was killed, but a warning for the injury.",
            "A mandatory license suspension for 1 year."
        ],
        explanation="Deliberately fleeing or attempting to evade a law enforcement officer is a serious crime. If someone is seriously injured during a police chase caused by a driver's attempt to escape, California law (Vehicle Code § 2800.3) makes it a felony punishable by imprisonment in state prison for three, five, or seven years, or by imprisonment in a county jail for not more than one year, and by a fine. This highlights that evading police can lead to felony charges when it endangers lives."
    )
]
section_traffic_laws = Quiz.Section("Traffic Laws and Regulations")
section_traffic_laws.questions.extend(traffic_laws_and_regulations_questions)
traffic_quiz_sections.append(section_traffic_laws)


# --- Category 2: Road Signs, Signals, and Markings ---
# Covers: Signs (shapes, colors, meanings), traffic signals (solid, flashing, blackout), pavement markings, curb colors.
road_signs_signals_and_markings_questions: List[qc.Question] = [
    qc.MultipleChoice(
        question="What does a curb painted BLUE indicate?",
        correct_answers=["Parking for disabled persons with a placard or special plate."],
        wrong_answers=[
            "Parking for loading/unloading passengers only.",
            "Parking for less than 15 minutes.",
            "Parking for emergency vehicles only.",
            "Anyone may park there for 15 minutes or less."
        ],
        explanation="Blue curbs designate parking spaces reserved exclusively for persons with disabilities who display a valid disabled person placard or special license plate. Parking in a blue zone without the proper authorization is illegal and can result in significant fines. White curbs are for passenger loading/unloading, and green curbs indicate time-limited parking."
    ),
    qc.MultipleChoice(
        question="What does a curb painted YELLOW indicate?",
        correct_answers=["Stop only long enough to load or unload passengers or freight."],
        wrong_answers=[
            "No stopping, standing, or parking at any time.",
            "Parking for disabled persons only.",
            "Short-term parking for up to 30 minutes (check posted signs).",
            "Parking permitted for any purpose after 6 PM."
        ],
        explanation="A yellow curb indicates a zone where stopping is permitted only for the active loading or unloading of freight or passengers. Drivers of non-commercial vehicles may typically stop briefly to load/unload passengers but should usually stay with the vehicle. Time limits may be posted and vary by local ordinance."
    ),
    qc.TrueFalseQuestion(
        question="True or False: A red curb means you can stop briefly to unload passengers if you stay with your vehicle.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. A curb painted red indicates that stopping, standing, or parking is prohibited at any time, for any reason (except for some transit buses at designated red bus zones). Red zones are often reserved for emergency access or to ensure clear visibility. Passenger loading is typically permitted at white curbs."
    ),
    qc.ShortAnswer(
        question="What color curb in California indicates a zone designated for parking for a limited amount of time?",
        correct_answer=["Green", "Green curb"],
        explanation="Green curbs, according to CVC 21458 and local ordinances, signify that parking is permitted, but only for a specific duration. The time limit is typically posted on a nearby sign or directly on the curb itself.",
        grading_instructions="Perfect score requires the color 'Green'. Mentioning 'Green curb' is also perfect. Any other color fails."
    ),
    qc.MultipleChoice(
        question="Two sets of solid double yellow lines spaced 2 feet or more apart indicate:",
        correct_answers=["A barrier that should not be crossed for any reason."],
        wrong_answers=[
            "Lanes of traffic moving in the same direction, passing allowed.",
            "A designated carpool (HOV) lane entrance or exit.",
            "You may cross them to make a left turn or U-turn if safe."
        ],
        explanation="Two sets of solid double yellow lines spaced two feet or more apart represent a solid barrier. Driving on, over, or making a left or U-turn across this marking is prohibited, except at specifically designated openings. It separates opposing lanes or areas where crossing is extremely unsafe."
    ),
    qc.MultipleChoice(
        question="A solid yellow line next to a broken yellow line on a two-lane roadway means:",
        correct_answers=["Vehicles next to the broken line may pass when safe; vehicles next to the solid line may not."],
        wrong_answers=[
            "Vehicles in both directions may pass with caution.",
            "Vehicles next to the solid line may pass if the way is clear.",
            "No passing is allowed from either direction."
        ],
        explanation="Pavement markings guide passing. A broken yellow line indicates passing is permitted from that lane when safe. A solid yellow line means passing is prohibited from that lane. When these are paired, only vehicles adjacent to the broken line may pass if the way is clear and it's safe to do so. Vehicles next to the solid line must not pass."
    ),
    qc.MultipleChoice(
        question="What does a flashing yellow traffic signal at an intersection mean?",
        correct_answers=["Slow down and proceed with caution, yielding if necessary."],
        wrong_answers=[
            "Stop completely before proceeding.",
            "The signal is about to turn red; prepare to stop.",
            "Speed up to clear the intersection quickly.",
            "Yield to all traffic on your right."
        ],
        explanation="A flashing yellow traffic signal means CAUTION. Drivers should slow down, be aware of their surroundings, check for cross-traffic and pedestrians, and proceed carefully through the intersection when safe. It does not require a full stop like a flashing red light but implies a need for heightened awareness."
    ),
    qc.MultipleChoice(
        question="What does a flashing red traffic light at an intersection mean?",
        correct_answers=["Stop, then proceed when it is safe (treat as a stop sign)."],
        wrong_answers=[
            "The traffic signal is about to turn green; prepare to go.",
            "Stop and do not proceed until a green light is shown.",
            "Slow down and check cross-traffic, proceeding without stopping if clear."
        ],
        explanation="A flashing red light means the same as a STOP sign. You must come to a complete stop, yield to any traffic and pedestrians, and proceed only when it's safe and your turn according to right-of-way rules."
    ),
    qc.MultipleChoice(
        question="A solid red traffic light indicates you should:",
        correct_answers=["Stop before the intersection or crosswalk and remain stopped until the light changes."],
        wrong_answers=["Proceed with caution if no cross-traffic is visible.", "Slow down, then proceed if the way is clear.", "Yield to oncoming traffic, then turn left."],
        explanation="A solid red light means you must come to a complete stop before the marked limit line, crosswalk, or intersection and remain stopped until the light turns green (or until you can legally make a turn on red after stopping, if permitted and safe)."
    ),
    qc.MultipleChoice(
        question="What should you do if you approach an intersection where the traffic signals are not working (blackout)?",
        correct_answers=["Treat the intersection as an all-way STOP: come to a stop, then proceed when safe."],
        wrong_answers=[
            "Proceed through the intersection at 15 mph without stopping.",
            "Treat the intersection as if it has a flashing yellow light.",
            "Ignore the traffic lights and follow only posted signs or pavement markings.",
            "The vehicle that arrives first has the right-of-way without stopping."
        ],
        explanation="If a traffic signal is completely out (black) due to power failure or malfunction, California law requires you to treat the intersection as if there are stop signs in all directions. Come to a full stop, then proceed cautiously, following the usual right-of-way rules for a four-way stop."
    ),
    qc.MultipleChoice(
        question="An 8-sided red sign (octagon) always means:",
        correct_answers=["Stop."],
        wrong_answers=[
            "Yield.",
            "Caution, hazard ahead.",
            "Railroad crossing."
        ],
        explanation="A red, octagonal (8-sided) sign is exclusively a STOP sign. You must make a full stop at the limit line, before the crosswalk, or before entering the intersection, then proceed when safe."
    ),
    qc.MultipleChoice(
        question="A 3-sided red and white triangular sign (pointed down) indicates:",
        correct_answers=["Yield."],
        wrong_answers=[
            "Stop.",
            "Do Not Enter.",
            "No Passing Zone."
        ],
        explanation="A downward-pointing triangular sign, red and white in color, universally signifies 'Yield'. Drivers must slow down or stop if necessary to give the right-of-way to traffic on the intersecting road or to pedestrians."
    ),
    qc.MultipleChoice(
        question="What does a square red-and-white sign stating \"DO NOT ENTER\" mean?",
        correct_answers=["You may not enter that lane or road from your direction; it is likely a one-way street against you or an exit ramp."],
        wrong_answers=[
            "The road is closed ahead for construction; find another route.",
            "Stop ahead and wait for an escort vehicle to guide you.",
            "Only emergency or construction vehicles may enter."
        ],
        explanation="A \"DO NOT ENTER\" sign, typically square or rectangular and red-and-white, indicates that entry into that roadway or lane is prohibited from your direction. This is often used for freeway off-ramps, one-way streets (at the exit end), or restricted access areas."
    ),
    qc.MultipleChoice(
        question="A red circle with a red diagonal slash over an action symbol on a sign means:",
        correct_answers=["The action or item inside the circle is prohibited."],
        wrong_answers=[
            "Warning: proceed with caution regarding the item in the circle.",
            "You must perform the action inside the circle.",
            "This is an informational sign about the circled item."
        ],
        explanation="A red circle with a red diagonal line through it universally means \"NO\" or that the action depicted by the symbol inside the circle is forbidden. For example, a U-turn arrow with a slash means \"No U-Turn.\""
    ),
    qc.MultipleChoice(
        question="A round yellow sign with a black \"X\" and the letters \"RR\" indicates:",
        correct_answers=["Railroad crossing ahead - slow down, look and listen for trains."],
        wrong_answers=[
            "Do not enter - road crosses itself ahead.",
            "An X-shaped intersection (crossroad) is ahead.",
            "Restricted road - only Rail Road company vehicles allowed.",
            "Stop Ahead"
        ],
        explanation="A circular yellow sign with a black \"X\" and \"RR\" is an advance warning for a railroad crossing. This unique shape and marking alerts drivers to slow down, look and listen for trains, and be prepared to stop if necessary."
    ),
    qc.MultipleChoice(
        question="A five-sided (pentagon-shaped) yellow or fluorescent yellow-green sign typically indicates:",
        correct_answers=["School zone or school crossing ahead - slow down and watch for children."],
        wrong_answers=[
            "General pedestrian crossing ahead.",
            "Playground nearby - watch for children at play.",
            "Children not allowed beyond this point without an adult.",
            "Hospital zone."
        ],
        explanation="A 5-sided (pentagon) sign is exclusively used to warn of a school zone or school crossing. When you see this sign, you should slow down, be extra alert for children, and obey any posted school zone speed limits (often 25 mph when children are present)."
    ),
    qc.MultipleChoice(
        question="A 4-sided diamond-shaped sign (usually yellow or orange) indicates:",
        correct_answers=["Warning of specific road conditions or hazards ahead."],
        wrong_answers=[
            "Regulatory instruction (must be obeyed, like a speed limit).",
            "A stop sign presented in a different shape.",
            "Guide sign for upcoming destinations or services."
        ],
        explanation="Diamond-shaped signs are warning signs. Yellow diamond signs alert you to potential hazards or changes in road conditions ahead (e.g., curves, intersections, slippery roads). Orange diamond signs typically warn of construction or maintenance work zones."
    ),
    qc.MultipleChoice(
        question="Orange-colored signs (often diamond-shaped) signify:",
        correct_answers=["Construction or maintenance work zone ahead - proceed with caution."],
        wrong_answers=[
            "General warning of wildlife or farm equipment on the road.",
            "A mandatory detour is required ahead.",
            "The road is permanently closed; you must turn around."
        ],
        explanation="Orange signs are used for construction and maintenance warnings. They alert drivers to work zones where there may be road workers, equipment, lane shifts, or temporary traffic controls. Slow down and be prepared for changes."
    ),
    qc.MultipleChoice(
        question="A yellow diamond sign depicting a car with wavy skid marks behind it indicates:",
        correct_answers=["Slippery when wet - reduce speed and use caution if the road is wet or icy."],
        wrong_answers=[
            "Bumpy or uneven road ahead - slow down.",
            "Road curves sharply ahead; use caution.",
            "Tire chains may be required ahead for snow.",
            "Winding road – several curves are coming."
        ],
        explanation="This sign warns that the road surface can become slippery, especially when wet or icy, increasing the risk of skidding. Reduce speed and avoid sudden maneuvers in such conditions."
    ),
    qc.MultipleChoice(
        question="A yellow diamond-shaped sign showing one straight vertical line with another line merging into it from the right side typically means:",
        correct_answers=["Lane ends ahead - traffic in the right lane must merge left."],
        wrong_answers=[
            "Two-way traffic begins ahead.",
            "A freeway exit lane is approaching on the right.",
            "An additional lane is beginning on the right; no merge necessary."
        ],
        explanation="This sign indicates a lane reduction, where the right lane is ending and traffic from that lane will need to merge into the continuing left lane. Drivers in both lanes should be prepared for this merge."
    ),
    qc.MultipleChoice(
        question="A yellow pennant-shaped sign on the left side of the road that reads \"No Passing Zone\" means:",
        correct_answers=["You are entering a no-passing zone - do not attempt to pass other vehicles."],
        wrong_answers=[
            "Overtaking or passing is allowed only during daylight hours in this zone.",
            "This sign marks the end of a no-passing zone; you may resume passing if safe.",
            "This is a one-way road; oncoming traffic is not expected, so passing is generally safe."
        ],
        explanation="A pennant-shaped (elongated triangle) yellow sign stating \"No Passing Zone\" is uniquely placed on the left side of the road to mark the beginning of a zone where passing is prohibited, usually due to limited sight distance (hills, curves) or other hazards. This supplements solid yellow line markings."
    ),
    qc.MultipleChoice(
        question="An orange triangular sign with red borders mounted on the back of a vehicle (e.g., tractor) indicates:",
        correct_answers=["It's a slow-moving vehicle that typically travels at 25 MPH or less."],
        wrong_answers=[
            "The vehicle is carrying hazardous materials.",
            "It's a right-of-way vehicle that can preempt traffic signals (like an emergency vehicle).",
            "The vehicle has an oversized or wide load.",
            "The vehicle is about to make a turn."
        ],
        explanation="This reflective orange triangle with a red border is a Slow-Moving Vehicle (SMV) emblem. It is displayed on vehicles (such as farm equipment or road maintenance machinery) that are designed to travel at speeds of 25 mph or less. Approach such vehicles with caution and be prepared to slow down significantly."
    ),
    qc.TrueFalseQuestion(
        question="True or False: Parking is never allowed in an area marked with crosshatched (diagonal) lines.",
        correct_answers=["True"],
        wrong_answers=["False"],
        explanation="True. Areas marked with crosshatched (diagonal) lines, often found next to disabled parking spaces (access aisles) or in other specially marked zones (e.g., gores, safety zones), indicate that parking, stopping, or driving in that area is prohibited at all times."
    )
]
section_road_signs = Quiz.Section("Road Signs, Signals, and Markings")
section_road_signs.questions.extend(road_signs_signals_and_markings_questions)
traffic_quiz_sections.append(section_road_signs)


# --- Category 3: Safe Driving Techniques ---
# Covers: Scanning, following distance, blind spots, tailgaters, adverse conditions (rain, fog), large trucks, highway hypnosis.
safe_driving_techniques_questions: List[qc.Question] = [
    qc.MultipleChoice(
        question="Which is a key safe driving practice regarding visual scanning?",
        correct_answers=["Constantly keep your eyes moving to scan the entire surroundings (ahead, sides, mirrors)."],
        wrong_answers=[
            "Stare only at the road directly in front of you.",
            "Focus primarily on your rearview mirror.",
            "Look mainly at the vehicle immediately ahead of you.",
            "Primarily focus on dashboard instruments."
        ],
        explanation="Safe driving requires continuous scanning of the entire environment: 10-15 seconds ahead, to the sides, and frequently checking mirrors (every 5-8 seconds). This allows drivers to identify potential hazards early and avoid tunnel vision. Staring only at one point leads to missing critical information."
    ),
    qc.ShortAnswer(
        question="Explain the '3-second rule' for following distance and state at least two conditions when you should increase this distance.",
        correct_answer=[
            "The 3-second rule measures a safe following distance. Pick a fixed object; when the vehicle ahead passes it, count 'one-thousand-one, one-thousand-two, one-thousand-three'. If you pass the object before finishing, you're too close.",
            "Increase distance in adverse conditions (rain, fog, ice), when following large trucks or motorcycles, when visibility is poor, when being tailgated, or on slippery roads."
        ],
        explanation="The 3-second rule helps estimate a safe following gap under good conditions. Watch the vehicle ahead pass a fixed point (sign, tree). Count how long it takes you to reach that same point. It should be at least 3 seconds. Increase this to 4 or more seconds in adverse weather (rain, fog, snow, ice), when following large trucks or motorcycles (which can obstruct your view or stop differently), when visibility is poor, if you are being tailgated, or if the road is slippery.",
        grading_instructions="Full credit requires explaining how to measure the 3-second gap (fixed point and counting) AND listing at least two specific conditions for increasing it. Partial credit for explaining purpose or only one component."
    ),
    qc.MultipleChoice(
        question="If you are being tailgated, the safest course of action is generally to:",
        correct_answers=["Change lanes when safe or slow down gradually to encourage the tailgater to pass."],
        wrong_answers=[
            "Tap your brakes sharply to warn the tailgater.",
            "Speed up significantly to create distance.",
            "Maintain your speed and lane position, ignoring the tailgater.",
            "Slam on your brakes to scare them."
        ],
        explanation="The safest way to handle a tailgater is to remove yourself from the situation if possible. If you can, change lanes to let them pass. If not, gradually reducing speed may encourage them to pass or at least increase your own forward space cushion, giving you more time to react if you need to stop. Tapping brakes (brake checking) can provoke aggression or cause a collision. Speeding up is also risky and may not deter the tailgater."
    ),
    qc.MultipleChoice(
        question="On a hot day, when are roads typically most slippery during a rainfall?",
        correct_answers=["For the first few minutes after rain begins."],
        wrong_answers=[
            "Immediately after the rain stops.",
            "After it has been raining continuously for an hour.",
            "Only during very heavy downpours."
        ],
        explanation="Road surfaces are usually most slippery during the first few minutes of rain, especially after a dry spell on a hot day. This is because oil, dust, and debris on the dry pavement mix with the initial rainwater, creating a slick film. This film is gradually washed away as the rain continues."
    ),
    qc.MultipleChoice(
        question="Large trucks have significant blind spots around them known as:",
        correct_answers=["No-Zones"],
        wrong_answers=[
            "Safe Zones",
            "Slow Zones",
            "Passing Zones",
            "Caution Areas"
        ],
        explanation="Large commercial trucks have extensive blind spots (No-Zones) to the front, rear, and sides where the truck driver's visibility is limited or non-existent. Drivers of smaller vehicles should avoid lingering in these areas because the truck driver likely cannot see them. If you can't see the truck driver in their side mirror, assume they can't see you."
    ),
    qc.MultipleChoice(
        question="When driving in fog, heavy rain, or snow, you should use:",
        correct_answers=["Low-beam headlights and reduce speed."],
        wrong_answers=[
            "High-beam headlights for better illumination.",
            "Only parking lights to avoid glare.",
            "Hazard flashers while maintaining normal speed.",
            "No lights if driving during the day."
        ],
        explanation="In fog, mist, heavy rain, snow, or dust, use your low-beam headlights. High-beams reflect off the precipitation/particles, causing glare and reducing your visibility. Also, reduce your speed and increase your following distance as visibility is impaired."
    ),
    qc.MultipleChoice(
        question="If an oncoming car at night has its high-beam headlights on, potentially blinding you, you should:",
        correct_answers=["Look toward the right edge of your lane (the fog line or shoulder) and slow down if needed."],
        wrong_answers=[
            "Close your eyes briefly until the car passes.",
            "Flash your own high beams repeatedly to signal them.",
            "Maintain your focus directly on the oncoming headlights to track the vehicle.",
            "Turn on your own high beams in retaliation."
        ],
        explanation="When an oncoming vehicle fails to dim its high beams, avoid staring directly at the glaring lights. Shift your gaze toward the right edge of your lane to use it as a guide, while still using your peripheral vision to monitor the other car. Slow down if necessary. Flashing your high beams can sometimes be misconstrued or escalate a situation, and focusing on the bright lights will impair your vision."
    ),
    qc.ShortAnswer(
        question="What is 'highway hypnosis' and what is a primary way to prevent it?",
        correct_answer=[
            "Highway hypnosis is a trance-like state or drowsiness caused by monotonous driving on long, straight roads.",
            "Prevent it by constantly keeping your eyes moving, scanning surroundings (mirrors, sides, far ahead, near), and taking regular breaks."
        ],
        explanation="Highway hypnosis occurs when a driver becomes drowsy or 'zones out' due to unchanging scenery and the steady rhythm of long-distance driving, reducing awareness and reaction time. The best prevention is active visual scanning: continuously moving your eyes. Taking breaks every couple of hours or 100 miles also helps combat fatigue.",
        grading_instructions="Full credit requires defining highway hypnosis (drowsiness/zoning out from monotony) AND stating the primary prevention as active eye scanning/taking breaks. Partial credit if only one part is correct."
    ),
    qc.MultipleChoice(
        question="Driving significantly slower than the general flow of freeway traffic:",
        correct_answers=["Can be dangerous as it may cause collisions or block traffic flow, especially in left lanes."],
        wrong_answers=[
            "Is always the safest option, regardless of lane.",
            "Is recommended in the far-left lane if you are unsure of your exit.",
            "Is legal as long as you are below the posted speed limit and in the right lane."
        ],
        explanation="While speeding is dangerous, driving much slower than surrounding traffic can also be hazardous, especially in middle or left lanes. It disrupts traffic flow and can lead to rear-end collisions or aggressive passing by other drivers. If you must drive slower, stay in the rightmost lane."
    ),
    qc.TrueFalseQuestion(
        question="True or False: Using cruise control is explicitly illegal on residential streets in California.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. While using cruise control on residential streets might be impractical or unsafe due to frequent speed changes, stops, and varying conditions, there is no specific California state law making it illegal. Drivers must always maintain a safe speed for conditions, whether using cruise control or not."
    )
]
section_safe_driving = Quiz.Section("Safe Driving Techniques")
section_safe_driving.questions.extend(safe_driving_techniques_questions)
traffic_quiz_sections.append(section_safe_driving)


# --- Category 4: Maneuvers and Parking ---
# Covers: Turning, passing, merging, lane usage, parking rules (uphill/downhill, hydrant).
maneuvers_and_parking_questions: List[qc.Question] = [
    qc.MultipleChoice(
        question="When are you legally allowed to drive off the paved roadway to pass another vehicle in California?",
        correct_answers=["Under no circumstances; it is always illegal."],
        wrong_answers=[
            "If the vehicle ahead is turning left and there is room on the shoulder.",
            "If there are two or more lanes available in your direction of travel.",
            "If you do not exceed the speed limit while passing.",
            "Only if the road is marked with a broken yellow line on your side and the shoulder is wide."
        ],
        explanation="Driving off the paved or main-traveled portion of the roadway to pass another vehicle is illegal under any circumstances in California. This maneuver is dangerous due to unpredictable surfaces, potential loss of control, and hazards to pedestrians or cyclists. You must stay on the paved roadway when passing."
    ),
    qc.MultipleChoice(
        question="When merging onto a freeway, you should be driving at what speed?",
        correct_answers=["At or near the speed of the freeway traffic."],
        wrong_answers=[
            "Significantly slower than the freeway traffic to be cautious.",
            "Significantly faster than the freeway traffic to find a gap quickly.",
            "The posted speed limit of the on-ramp, regardless of freeway traffic speed."
        ],
        explanation="When entering a highway, use the acceleration lane to build up speed to match the flow of traffic already on the freeway. Merging too slowly can disrupt traffic flow and create a hazard for vehicles behind you. Merging too fast can also be dangerous. The goal is to blend in smoothly and safely."
    ),
    qc.MultipleChoice(
        question="You are approaching an intersection with a green light, but traffic is backed up and blocking the far side. You should:",
        correct_answers=["Stay out of the intersection until you can clear it completely."],
        wrong_answers=[
            "Enter the intersection partially to hold your spot.",
            "Drive onto the shoulder or into another lane to get around the traffic.",
            "Proceed into the intersection because you have the green light.",
            "Honk to make others move."
        ],
        explanation="Drivers must not enter an intersection, even on a green light, unless they can pass completely through without stopping and blocking traffic or crosswalks. Blocking the intersection ('blocking the box') is illegal, impedes cross-traffic, and can cause gridlock."
    ),
    qc.MultipleChoice(
        question="When parking uphill on a two-way street WITH a curb, which way should your front wheels be turned?",
        correct_answers=["Away from the curb (to the left)."],
        wrong_answers=[
            "Toward the curb (to the right).",
            "Straight ahead, with the parking brake firmly set.",
            "It doesn't matter as long as the parking brake is engaged."
        ],
        explanation="When parking uphill with a curb, turn your front wheels AWAY from the curb (to the left). Let the vehicle roll back slightly until the rear of the front wheel gently touches the curb. This way, if the brakes fail, the curb will help stop the vehicle from rolling into traffic. Mnemonic: 'Up-Up and Away'."
    ),
    qc.MultipleChoice(
        question="When parking downhill on a street WITH a curb, which way should you turn your front wheels?",
        correct_answers=["Towards the curb (to the right)."],
        wrong_answers=[
            "Away from the curb (to the left).",
            "Straight ahead.",
            "Parallel to the curb, ensuring tires do not touch it."
        ],
        explanation="When parking downhill with a curb, turn your front wheels INTO the curb (to the right). This ensures that if the brakes fail, the curb will act as a block and help stop the car from rolling into traffic. Mnemonic: 'Down-Right Towards'."
    ),
    qc.TrueFalseQuestion(
        question="True or False: When parking uphill or downhill where there is NO curb, you should turn your front wheels toward the side of the road (away from traffic).",
        correct_answers=["True"],
        wrong_answers=["False"],
        explanation="True. When parking on a hill (uphill or downhill) without a curb, always turn your front wheels toward the side of the road (the shoulder or edge, usually to the right). This ensures that if the vehicle rolls, it will move away from the center of the road and traffic."
    ),
    qc.MultipleChoice(
        question="When making a left turn from a one-way street onto another one-way street, you should start your turn from:",
        correct_answers=["The far-left traffic lane."],
        wrong_answers=[
            "The lane closest to the right curb.",
            "Any available lane, as long as you signal.",
            "The center lane, if one exists, for better visibility."
        ],
        explanation="To turn left from a one-way street onto another one-way street, you must position your vehicle in the traffic lane furthest to the left (closest to the left curb) before beginning the turn. You should also end your turn in a lane appropriate for a left turn on the new one-way street."
    ),
    qc.TrueFalseQuestion(
        question="True or False: You can legally make a left turn on a red light from a two-way street onto a one-way street in California after stopping.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. In California, a left turn on a red light is only permitted from a one-way street onto another one-way street, after a complete stop and yielding to traffic and pedestrians, unless a sign prohibits it. It is illegal to turn left on red from a two-way street."
    ),
    qc.ShortAnswer(
        question="In California, what is the minimum distance you must continuously signal before making a turn or changing lanes under normal conditions?",
        correct_answer=["100 feet", "One hundred feet"],
        explanation="California Vehicle Code (CVC) 22108 requires drivers to signal continuously during the last 100 feet traveled before turning or changing lanes. This provides adequate warning to other road users.",
        grading_instructions="Perfect score requires '100' and 'feet'. '100' alone gets partial credit. Other numbers fail."
    ),
    qc.ShortAnswer(
        question="What is the minimum distance you must park away from a fire hydrant in California?",
        correct_answer=["15 feet", "Fifteen feet"],
        explanation="CVC 22514 prohibits parking within 15 feet of a fire hydrant (on either side). This clear space is essential for fire department access during emergencies.",
        grading_instructions="Perfect score for '15' and 'feet'. '15' alone gets partial credit. Other numbers fail."
    ),
    qc.MultipleChoice(
        question="When parallel parking in California, how close should your vehicle's wheels be to the curb when finished?",
        correct_answers=["Within 18 inches."],
        wrong_answers=[
            "Touching the curb lightly.",
            "Within 6 inches.",
            "Within 24 inches, but no more.",
            "As close as possible without touching."
        ],
        explanation="When correctly parallel parked, California law (CVC 22502(a)) generally requires your vehicle's right-hand wheels to be parallel to and within 18 inches of the right-hand curb (or left-hand curb on a one-way street)."
    ),
    qc.MultipleChoice(
        question="On a freeway with multiple lanes in your direction, which lane should you generally use for slower driving or preparing to exit?",
        correct_answers=["The far right lane."],
        wrong_answers=[
            "The left (fast) lane.",
            "The lane that has the smoothest flow of traffic, regardless of position.",
            "Any lane, as long as you are at or below the speed limit."
        ],
        explanation="On a multi-lane highway, slower-moving traffic should stay in the rightmost lane. The left lane(s) are for faster traffic and passing. The far right lane is also typically used by vehicles entering and exiting the freeway. If you are driving slower than other traffic, move to the right."
    ),
    qc.MultipleChoice(
        question="When waiting at an intersection to make a left turn, how should you position your vehicle's front wheels?",
        correct_answers=["Keep your front wheels pointed straight ahead until you actually begin the turn."],
        wrong_answers=[
            "Turn your wheels to the left to prepare for a quick turn.",
            "Angle your car slightly into the intersection with wheels turned left.",
            "It doesn't matter as long as you are behind the limit line."
        ],
        explanation="While waiting to turn left (e.g., at a green light with oncoming traffic), keep your front wheels pointed straight ahead. If your wheels are already turned left and you are rear-ended, your car could be pushed into oncoming traffic. Only turn your wheels when you are ready and it's safe to make the turn."
    ),
    qc.MultipleChoice(
        question="On a typical two-lane road (one lane in each direction), where should you generally pass other vehicles?",
        correct_answers=["On the left, when safe and legal to do so."],
        wrong_answers=[
            "On the right, if there is space on the shoulder.",
            "On the shoulder of the road.",
            "Whichever side appears clearer and has more space."
        ],
        explanation="On a typical two-lane road with traffic moving in opposite directions, passing must be done on the left. This involves entering the oncoming traffic lane, so it must only be done when it is safe (clear view, no oncoming traffic) and legal (indicated by pavement markings like a broken yellow line on your side, and no 'No Passing Zone' signs)."
    )
]
section_maneuvers_parking = Quiz.Section("Maneuvers and Parking")
section_maneuvers_parking.questions.extend(maneuvers_and_parking_questions)
traffic_quiz_sections.append(section_maneuvers_parking)


# --- Category 5: Emergency Procedures and Vehicle Handling ---
# Covers: Tire blowouts, brake failures, accelerator sticking, skids.
emergency_procedures_questions: List[qc.Question] = [
    qc.ShortAnswer(
        question="Describe the correct immediate procedure for handling a tire blowout while driving.",
        correct_answer=[
            "Grip the steering wheel firmly and keep the vehicle going straight.",
            "Do NOT brake hard; ease off the accelerator gradually.",
            "Let the vehicle slow down on its own or with very gentle braking once stable.",
            "Once speed is reduced and control is maintained, steer to a safe location off the road."
        ],
        explanation="If a tire blows out: 1. Grip the steering wheel firmly to maintain control as the car may pull to one side. 2. Do NOT slam on the brakes; this can cause a loss of control. 3. Ease off the accelerator and let the vehicle slow down gradually. 4. Once the car has slowed and is under control, brake gently and steer to a safe place to stop, well off the roadway. Activate hazard lights.",
        grading_instructions="Full credit requires mentioning: 1) Firm grip on steering/keep straight, 2) Ease off gas (NOT braking hard), 3) Letting car slow gradually before gentle braking, and 4) Steering safely off road. Emphasizing *not* braking hard is critical."
    ),
    qc.MultipleChoice(
        question="If your accelerator (gas pedal) sticks while driving, what is the recommended first primary action?",
        correct_answers=["Shift the vehicle into Neutral and then apply the brakes."],
        wrong_answers=[
            "Turn off the ignition immediately while the car is moving.",
            "Try to pry the pedal up with your foot or hand while still in Drive.",
            "Pump the gas pedal rapidly to try to unstick it.",
            "Apply the parking brake forcefully."
        ],
        explanation="If the accelerator sticks: 1. Shift the transmission into Neutral. This disconnects the engine's power from the wheels, even if the engine is racing. 2. Apply the brakes firmly to slow down. 3. Steer to a safe location off the road. 4. Once stopped, turn off the ignition. Turning off the engine while moving can disable power steering and power brakes, making control difficult."
    ),
    qc.MultipleChoice(
        question="If your brakes suddenly fail while driving, what is the generally recommended first action to take?",
        correct_answers=["Pump the brake pedal rapidly several times."],
        wrong_answers=[
            "Immediately shift into Park.",
            "Shut off the engine while the vehicle is still moving at speed.",
            "Swerve sharply from side to side to create friction and slow down.",
            "Apply the parking brake as hard as possible."
        ],
        explanation="If your brakes fail: 1. Pump the brake pedal rapidly and firmly. This may build up enough hydraulic pressure to activate the brakes, even if partially. 2. If pumping doesn't work, downshift to a lower gear (engine braking). 3. Apply the parking/emergency brake gradually and carefully (applying too hard can lock the wheels and cause a skid). 4. Steer to a safe place and, if necessary, look for ways to slow down like rubbing tires against a curb (as a last resort)."
    ),
    qc.MultipleChoice(
        question="If your vehicle starts to skid on a slippery road (e.g., rear wheels lose traction), what should you generally do first?",
        correct_answers=["Take your foot off the accelerator (and avoid braking) and steer in the direction you want the front of the car to go (often the direction of the skid)."],
        wrong_answers=[
            "Brake hard and hold the brake pedal down firmly.",
            "Pump the brakes rapidly and steer sharply opposite the direction of the skid.",
            "Engage your parking brake immediately to stop the rear wheels.",
            "Accelerate slightly to try to power out of the skid."
        ],
        explanation="When your car begins to skid: 1. Ease your foot off the accelerator. 2. Avoid braking suddenly, as this can make the skid worse. 3. Steer gently in the direction you want the front of the car to go. For a rear-wheel skid, this means steering in the direction the rear of the car is sliding (e.g., if rear skids right, steer right). Look where you want to go and steer smoothly."
    ),
    qc.TrueFalseQuestion(
        question="True or False: In a rear-wheel skid, you should steer in the opposite direction the rear of the car is sliding to correct it.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. If the rear wheels start to skid ('fishtail'), you should steer in the same direction that the rear of the car is sliding ('steer into the skid') to help straighten the vehicle and regain traction."
    ),
    qc.MultipleChoice(
        question="To regain control during a front-wheel skid (understeer, where the car continues straight despite turning the wheel), you should primarily:",
        correct_answers=["Ease off the accelerator and/or brake gently until traction returns, making smooth steering adjustments."],
        wrong_answers=[
            "Steer sharply in the desired direction repeatedly.",
            "Apply the parking brake to shift weight.",
            "Accelerate harder to pull the front wheels through the turn.",
            "Shift to a lower gear immediately."
        ],
        explanation="In a front-wheel skid (understeer), the front tires have lost traction and are not responding to steering input. The primary action is to reduce demand on the front tires by easing off the gas and/or brake gently. This allows them to regain grip. Steering adjustments should be smooth and correspond to where you want to go as traction returns."
    ),
    qc.ShortAnswer(
        question="Besides shifting to neutral and braking, what is one other method to help slow down if your brakes completely fail?",
        correct_answer=[
            "Use the parking/emergency brake (gradually).",
            "Downshift to a lower gear (engine braking).",
            "Scrape tires against a curb (last resort).",
            "Steer uphill if possible (last resort)."
        ],
        explanation="If pumping the brakes doesn't work, and after attempting to shift to neutral/lower gear for engine braking, you can gradually apply the parking/emergency brake. As a last resort in extreme situations, carefully scraping tires against a curb or steering onto an uphill slope can help dissipate speed. Sounding your horn and flashing lights can also warn others.",
        grading_instructions="Full credit for mentioning gradual use of the parking brake OR downshifting OR scraping curb/steering uphill (if not already implied by 'braking')."
    )
]
section_emergency_handling = Quiz.Section("Emergency Procedures and Vehicle Handling")
section_emergency_handling.questions.extend(emergency_procedures_questions)
traffic_quiz_sections.append(section_emergency_handling)


# --- Category 6: Accidents, Reporting, and DMV Responsibilities ---
# Covers: Collision reporting (SR-1), actions after collision, DMV notifications (selling, address).
accidents_reporting_dmv_questions: List[qc.Question] = [
    qc.MultipleChoice(
        question="Within how many days must you notify the DMV after selling or transferring ownership of your vehicle in California?",
        correct_answers=["5 days"],
        wrong_answers=[
            "10 days",
            "30 days",
            "There is no specific time limit as long as the new owner registers it."
        ],
        explanation="When a California-registered vehicle is sold or transferred, the seller is legally required to notify the DMV within 5 calendar days by submitting a Notice of Transfer and Release of Liability (NRL). This protects the seller from future liability (parking tickets, accidents) related to the vehicle."
    ),
    qc.MultipleChoice(
        question="You are required to file an SR-1 report with the DMV within 10 days if you are involved in a collision in California that results in:",
        correct_answers=["Property damage over $1,000 or any injury/death."],
        wrong_answers=[
            "Any property damage, regardless of the amount.",
            "Only if the collision results in a death or severe injury.",
            "Only if you are found to be at fault for the collision.",
            "If the police file a report, you do not need to file an SR-1."
        ],
        explanation="California law requires drivers involved in a collision to file a Report of Traffic Accident Occurring in California (SR-1) form with the DMV within 10 days if the collision caused property damage exceeding $1,000, or resulted in any injury (no matter how minor) or death. This applies regardless of who was at fault, and even if law enforcement also files a report."
    ),
    qc.ShortAnswer(
        question="If you are involved in a minor traffic collision in California with no injuries, list one essential piece of identifying information you must exchange with the other driver(s).",
        correct_answer=[
            "Driver's license information (name, address, license number)",
            "Vehicle registration information (owner name, address, plate number)",
            "Proof of financial responsibility (insurance company name and policy number)",
            "Current name and address of driver and registered owner"
        ],
        explanation="After ensuring safety, CVC 16025 requires drivers involved in any collision resulting in property damage to exchange key information. This includes their full name, current address, driver's license number, vehicle registration number, and proof of financial responsibility (typically insurance company name and policy number).",
        grading_instructions="Perfect score for naming any ONE of the following clearly: Driver's license (or DL info/number), Registration info (or plate/owner), Insurance info (or policy/company), Full Name and Address. 'Contact info' generally gets partial credit."
    ),
    qc.ShortAnswer(
        question="What are the two key actions required by California law if you hit an unoccupied parked car and cannot find the owner?",
        correct_answer=[
            "Leave a written note with your name, address, phone number, and a brief explanation of the accident, securely attached to the vehicle.",
            "Report the collision to local law enforcement (police or CHP) without unnecessary delay."
        ],
        explanation="If you collide with an unoccupied parked vehicle, California law requires you to: 1. Securely leave a written note on the damaged vehicle containing your name, address, phone number, and a statement of the circumstances. 2. Report the accident to the appropriate local police department or the California Highway Patrol (CHP) without unnecessary delay.",
        grading_instructions="Full credit requires mentioning both leaving a comprehensive note AND reporting to law enforcement. Partial credit for mentioning only one, or an incomplete note. No credit if neither key action is mentioned."
    ),
    qc.TrueFalseQuestion(
        question="True or False: If you damage unattended property (like a fence) and cannot find the owner, you are not required to report it to law enforcement if the damage seems less than $1000.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. If you damage any property (parked car, fence, mailbox, etc.) and cannot locate the owner, you must leave a note with your contact information AND report the incident to law enforcement, regardless of the apparent damage amount. Failing to do so can be considered a hit-and-run."
    ),
    qc.TrueFalseQuestion(
        question="True or False: If you are involved in a minor, non-injury collision, you are legally required to move your vehicle out of the traffic lanes if it is safe to do so and the vehicle is drivable.",
        correct_answers=["True"],
        wrong_answers=["False"],
        explanation="True. California's 'Move Over' law for minor accidents (CVC 20002, 20001 when applicable to property damage) encourages or requires drivers involved in minor, non-injury collisions to move their vehicles out of the travel lanes to a safe location (like the shoulder) if the vehicle is drivable and it's safe to do so. This helps prevent secondary accidents and traffic congestion."
    )
]
section_accidents_dmv = Quiz.Section("Accidents, Reporting, and DMV Responsibilities")
section_accidents_dmv.questions.extend(accidents_reporting_dmv_questions)
traffic_quiz_sections.append(section_accidents_dmv)


# --- Category 7: Vulnerable Road Users and Special Conditions ---
# Covers: Pedestrians, bicyclists, school buses, child safety restraints, railroad crossings, construction zones.
vulnerable_road_users_questions: List[qc.Question] = [
    qc.MultipleChoice(
        question="What is the speed limit within 100 feet of an uncontrolled railroad crossing where you cannot see 400 feet down the tracks in both directions?",
        correct_answers=["15 mph"],
        wrong_answers=[
            "10 mph",
            "25 mph",
            "The same as the surrounding area's posted speed limit."
        ],
        explanation="The California Driver's Handbook specifies a speed limit of 15 mph when you are within 100 feet of a railroad crossing that is not controlled by gates, signals, or a flagman, AND your view down the tracks is limited to less than 400 feet in both directions. This reduced speed allows more time to react to an approaching train."
    ),
    qc.MultipleChoice(
        question="When making a right turn where a bicycle lane is present, you should:",
        correct_answers=["Signal, check for bicyclists, and merge into the bicycle lane within 200 feet before the turn, then turn from the bike lane."],
        wrong_answers=[
            "Make the turn from the vehicle lane, yielding to any bicyclists in the bike lane as you cross it.",
            "Wait until after the intersection to enter the bike lane if your path is clear.",
            "Honk to alert bicyclists and then proceed to turn from your lane.",
            "Never enter a bicycle lane with a motor vehicle."
        ],
        explanation="When preparing for a right turn adjacent to a bike lane, drivers should signal, carefully check for bicyclists (including over the shoulder), and if clear, merge into the bike lane no more than 200 feet before the intersection. The turn is then executed from the bike lane. Do not cut off bicyclists."
    ),
    qc.MultipleChoice(
        question="If traffic is slow and heavy, when should you proceed across railroad tracks?",
        correct_answers=["Only when you are sure you can completely clear the tracks without stopping on them."],
        wrong_answers=[
            "As soon as the vehicle ahead of you starts moving, even if there isn't much space.",
            "When the warning lights stop flashing, even if traffic is stopped just beyond the tracks.",
            "Immediately after a train has passed, assuming another isn't coming.",
            "If you can clear at least half of your vehicle over the tracks."
        ],
        explanation="Never start to cross railroad tracks unless you are certain you have enough room to get completely across without stopping. If traffic ahead is slow or stopped, preventing you from clearing the tracks, you must wait before the tracks (before the limit line or at least 15 feet away). Stopping on the tracks is extremely dangerous as a train could arrive."
    ),
    qc.MultipleChoice(
        question="When approaching a school bus with flashing YELLOW lights, you must:",
        correct_answers=["Slow down and prepare to stop, as the bus is likely about to stop and activate red lights."],
        wrong_answers=[
            "Stop immediately at least 25 feet behind the bus.",
            "Proceed past the bus at a reduced speed if no children are visible.",
            "Maintain your speed but watch for children.",
            "Change lanes and pass the bus quickly."
        ],
        explanation="Flashing yellow lights on a school bus serve as a warning that the bus is preparing to stop to load or unload children. Drivers must slow down and be ready to stop when they see these lights. Soon after, the bus will typically display flashing red lights and extend a stop arm, at which point drivers (in applicable lanes) must stop."
    ),
    qc.MultipleChoice(
        question="A school bus ahead of you in your lane is stopped with flashing RED lights. What should you do (assuming a non-divided, two-lane road)?",
        correct_answers=["Stop and remain stopped as long as the red lights are flashing."],
        wrong_answers=[
            "Slow down to 10 mph and pass the bus with caution if no children are crossing.",
            "Change lanes to the left and proceed slowly past the bus.",
            "Stop, then proceed if you determine no children are present around the bus.",
            "Honk to ensure children are aware of your vehicle before passing."
        ],
        explanation="Flashing red lights on a school bus (and often an extended stop arm) mean the bus is actively loading or unloading children. On a two-way street or a highway not divided by a median, traffic in both directions must stop and remain stopped as long as the red lights are flashing. Do not proceed until the lights stop and the bus begins to move. The only exception is if you are on the opposite side of a divided highway or a multilane highway with two or more lanes in each direction."
    ),
    qc.TrueFalseQuestion(
        question="True or False: You must yield the right-of-way to a pedestrian crossing the street even if there is no marked crosswalk at an intersection.",
        correct_answers=["True"],
        wrong_answers=["False"],
        explanation="True. Drivers must yield to pedestrians crossing the roadway within any marked or unmarked crosswalk at an intersection. Pedestrians have the right-of-way in these situations, and drivers must exercise due care."
    ),
    qc.MultipleChoice(
        question="When passing a bicyclist on the road, California law requires you to provide a minimum distance of:",
        correct_answers=["3 feet."],
        wrong_answers=[
            "1 foot.",
            "5 feet.",
            "One full car width.",
            "Enough space so you don't feel them."
        ],
        explanation="California's 'Three Feet for Safety Act' requires drivers to maintain a minimum distance of three feet when passing a bicyclist traveling in the same direction. If unable to provide three feet due to traffic or roadway conditions, the driver must slow to a reasonable and prudent speed and only pass when the bicyclist will not be endangered."
    ),
    qc.MultipleChoice(
        question="Children under 2 years old must ride in a rear-facing car seat in California unless:",
        correct_answers=["They weigh 40 pounds or more OR are 40 inches or taller."],
        wrong_answers=[
            "They can sit up unassisted for at least 10 minutes.",
            "The vehicle has no functional back seat.",
            "They are accompanied by an adult in the back seat.",
            "They have reached their first birthday."
        ],
        explanation="California law requires children under 2 years old to be secured in a rear-facing child restraint system in the back seat unless they meet specific exceptions: weighing 40 pounds or more, OR being 40 inches tall or taller."
    ),
    qc.TrueFalseQuestion(
        question="True or False: A child who is 8 years old but only 4'6\" tall can legally use a regular vehicle seat belt in California without a booster seat.",
        correct_answers=["False"],
        wrong_answers=["True"],
        explanation="False. Children in California must remain in a booster seat or other appropriate child passenger restraint system until they are 8 years old OR reach a height of 4 feet 9 inches. Since this child is 8 years old but shorter than 4'9\", they must continue using a booster seat until the vehicle's safety belt fits them properly (lap belt low on the hips, shoulder belt across the center of the shoulder and chest)."
    ),
    qc.ShortAnswer(
        question="According to California law, who is primarily responsible for ensuring passengers under 16 years old are properly secured with a seatbelt or child restraint?",
        correct_answer=["The driver of the vehicle."],
        explanation="The driver of the vehicle is legally responsible for making sure that all passengers under the age of 16 are properly secured using an appropriate child restraint system (if applicable based on age, weight, and height) or a seatbelt.",
        grading_instructions="Full credit requires stating 'The driver' or 'Driver'. No credit for other answers like 'parents' or 'the passenger themselves' for this age group."
    ),
    qc.MultipleChoice(
        question="You see a signal person (flagger) at a construction site ahead. You should obey their instructions:",
        correct_answers=["At all times, even if their instructions contradict existing signs or signals."],
        wrong_answers=[
            "Only if they appear to be an official law enforcement officer.",
            "Only if their instructions match the posted traffic signs.",
            "Only during daylight hours; at night, follow standard signals."
        ],
        explanation="Drivers must obey the instructions or signals given by any authorized flagger or traffic control person at all times. Their directions override standard signs, signals, and pavement markings in a temporary traffic control zone."
    ),
    qc.ShortAnswer(
        question="What should you do at an uncontrolled railroad crossing where visibility is poor (e.g., you cannot see 400 feet down the tracks in both directions)?",
        correct_answer=["Slow down to 15 mph when within 100 feet of the crossing, look and listen carefully, and be prepared to stop if a train is approaching."],
        explanation="At uncontrolled railroad crossings with poor visibility (less than 400 feet in both directions), you must slow to 15 mph within 100 feet of the tracks. Look and listen carefully for an approaching train and be prepared to stop at least 15 feet from the nearest rail if necessary. Never proceed unless you are sure no train is coming.",
        grading_instructions="Full credit if speed (15 mph within 100ft) and action (look, listen, prepare to stop) for limited visibility are both included. Partial for one component. No credit if they suggest no special action is needed."
    )
]
section_vulnerable_users = Quiz.Section("Vulnerable Road Users and Special Conditions")
section_vulnerable_users.questions.extend(vulnerable_road_users_questions)
traffic_quiz_sections.append(section_vulnerable_users)


# Create the Quiz object
quiz_traffic_laws = Quiz(section_bank=traffic_quiz_sections, source_material=source_material_traffic_laws, title="California DMV Practice Test")

# --- Quiz: AP US History ---
ap_us_history_sections = []

# Section: Basics
section_apush_basics = Quiz.Section("Basics")
section_apush_basics.questions.extend([
    qc.MultipleChoice(
        question="The AP US History course spans from which years?",
        correct_answers=['1491 to the present day'],
        wrong_answers=['1607 to 1898', '1776 to 1945', '1865 to 2000'],
        explanation="The APUSH course covers American history from 1491 to the present."
    ),
    qc.TrueFalseQuestion(
        question="The AP US History exam typically sees over 50% of students scoring a 3 or higher.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="Typically less than 50% of students achieve a score of 3 or higher on the APUSH exam."
    ),
    qc.ShortAnswer(
        question="Name one of the historical thinking skills emphasized in the APUSH course.",
        correct_answer=["Comparison", "Causation", "Continuity and Change over Time", "Contextualization", "Argumentation", "Using Evidence", "Interpretation", "Synthesis"], # Added example answers
        explanation="Historical thinking skills are assessed through various question formats. Key skills include comparison, causation, continuity and change, contextualization, argumentation, using evidence, interpretation, and synthesis.",
        grading_instructions="Accept any valid historical thinking skill relevant to APUSH. Be detailed and accurate."
    )
])
ap_us_history_sections.append(section_apush_basics)

# Section: Period 1: 1491-1607
section_apush_period1 = Quiz.Section("Period 1: 1491-1607")
section_apush_period1.questions.extend([
    qc.MultipleChoice(
        question="Which of the following crops was pivotal in supporting large-scale, sedentary civilizations like the Mound Builders?",
        correct_answers=['Maize'],
        wrong_answers=['Barley', 'Rice', 'Wheat'],
        explanation="The cultivation of maize (corn) supported large-scale civilizations in North America before European contact."
    ),
    qc.TrueFalseQuestion(
        question="European exploration was solely driven by the desire for gold and silver.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="European exploration was driven by a combination of factors, often summarized as 'God, Gold, and Glory,' which included religious conversion, wealth acquisition, and national prestige."
    ),
    qc.ShortAnswer(
        question="What is the Columbian Exchange?",
        correct_answer=["The widespread transfer of plants, animals, culture, human populations, technology, diseases, and ideas between the Americas, West Africa, and the Old World (Europe) in the 15th and 16th centuries."],
        explanation="The Columbian Exchange involved the widespread transfer of plants, animals, culture, human populations, technology, diseases, and ideas between the Americas (New World), West Africa, and the Old World (Europe) following Columbus's voyages.",
        grading_instructions="Answer should mention the exchange of goods/diseases/ideas between Old and New Worlds. Be detailed and accurate."
    ),
    qc.MultipleChoice(
        question="What was the primary impact of European diseases on Native American populations during the Columbian Exchange?",
        correct_answers=['Devastating demographic decline'],
        wrong_answers=['Cultural exchange', 'Economic prosperity', 'Increased immunity'],
        explanation="European diseases, to which Native Americans had no immunity, caused widespread epidemics that decimated indigenous communities, leading to a massive population decline."
    ),
    qc.MultipleChoice(
        question="What system granted conquistadors control over Native American labor and tribute?",
        correct_answers=['Encomienda system'],
        wrong_answers=['Indentured servitude', 'Repartimiento system', 'Slavery'],
        explanation="The encomienda system was a Spanish labor system that rewarded conquerors with the labor of particular groups of conquered non-Christian people."
    )
])
ap_us_history_sections.append(section_apush_period1)

# Section: Period 2: 1607-1754
section_apush_period2 = Quiz.Section("Period 2: 1607-1754")
section_apush_period2.questions.extend([
    qc.MultipleChoice(
        question="Which European power attracted a comparatively large number of migrants seeking religious freedoms and improved living conditions to its North American colonies?",
        correct_answers=['British'],
        wrong_answers=['Dutch', 'French', 'Spanish'],
        explanation="The British colonies, particularly New England and Pennsylvania, attracted significant numbers of migrants seeking religious freedom and economic opportunities."
    ),
    qc.TrueFalseQuestion(
        question="The New England colonies primarily focused on exporting labor-intensive staple crops like tobacco.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="The Chesapeake colonies (like Virginia and Maryland) and Southern Atlantic colonies focused on staple crops like tobacco and rice. New England colonies had a more diversified economy including fishing, shipbuilding, and small farming."
    ),
    qc.ShortAnswer(
        question="What was mercantilism?",
        correct_answer=["An economic policy designed to maximize the exports and minimize the imports for an economy. It promotes imperialism, tariffs and subsidies on traded goods to achieve that goal."],
        explanation="Mercantilism was an economic theory and practice, dominant in Europe from the 16th to the 18th century, that promoted governmental regulation of a nation's economy for the purpose of augmenting state power at the expense of rival national powers. It aimed to maintain a favorable balance of trade, where exports exceeded imports, often through the accumulation of colonies.",
        grading_instructions="Answer should mention state control of economy for national power, favorable balance of trade, or use of colonies. Be detailed and accurate."
    ),
    qc.TrueFalseQuestion(
        question="William Penn's Pennsylvania was known for its peaceful relations with Native Americans during its early years.",
        correct_answers=['True'],
        wrong_answers=['False'],
        explanation="Pennsylvania, under William Penn, initially purchased land from Native Americans and aimed for fair treatment and peaceful coexistence, which was relatively unique among the colonies at the time."
    ),
    qc.TrueFalseQuestion(
        question="Indentured servants in the early American colonies were always African.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="Indentured servants in the early American colonies were predominantly white Europeans, mostly male, who contracted to work for a number of years in exchange for passage to the New World."
    )
])
ap_us_history_sections.append(section_apush_period2)

# Section: Period 3: 1754-1800
section_apush_period3 = Quiz.Section("Period 3: 1754-1800")
section_apush_period3.questions.extend([
    qc.MultipleChoice(
        question="Which war resulted in massive debts for Britain, leading to new taxation policies imposed on the American colonies?",
        correct_answers=["Seven Years' War"], # Also known as French and Indian War in North America
        wrong_answers=['American Civil War', 'War of 1812', 'World War I'],
        explanation="The Seven Years' War (1756-1763), known as the French and Indian War in its North American theater, led to significant British debt, which Britain attempted to recoup through new taxes on the American colonies."
    ),
    qc.TrueFalseQuestion(
        question="The Intolerable Acts were perceived by many colonists as a direct and unacceptable assault on their rights and liberties.",
        correct_answers=['True'],
        wrong_answers=['False'],
        explanation="The Intolerable Acts (Coercive Acts) were a series of punitive laws passed by the British Parliament in 1774 after the Boston Tea Party. They were widely seen by the colonists as a violation of their constitutional rights, their colonial charters, and their colonial liberties."
    ),
    qc.ShortAnswer(
        question="What were the Articles of Confederation?",
        correct_answer=["The first government framework (constitution) of the United States, adopted during the Revolutionary War."],
        explanation="The Articles of Confederation and Perpetual Union was an agreement among the 13 original states of the United States of America that served as its first frame of government. It was approved by the Second Continental Congress in 1777 and went into effect in 1781. It suffered from major weaknesses, such as a weak central government.",
        grading_instructions="Answer should identify it as the first US government/constitution and note its weaknesses. Be detailed and accurate."
    ),
    qc.ShortAnswer(
        question="What was a main grievance of the American colonists that led to the American Revolution?",
        correct_answer=["Taxation without representation"],
        explanation="A central grievance of the colonists was 'taxation without representation,' meaning they were being taxed by the British Parliament but had no elected representatives in that Parliament to voice their interests.",
        grading_instructions="Mention 'taxation without representation' or lack of consent in governance. Be detailed and accurate."
    ),
    qc.MultipleChoice(
        question="Which American diplomat was instrumental in securing French support during the American Revolution?",
        correct_answers=['Benjamin Franklin'],
        wrong_answers=['George Washington', 'John Adams', 'Thomas Jefferson'],
        explanation="Benjamin Franklin played a crucial diplomatic role in securing an alliance with France, which was vital to the American victory in the Revolutionary War."
    ),
    qc.TrueFalseQuestion(
        question="The Boston Tea Party was largely perceived by the British government as a minor, non-violent protest with little consequence.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="The Boston Tea Party was seen by the British government as a deliberate act of defiance and destruction of property, leading directly to the passage of the punitive Intolerable (Coercive) Acts."
    ),
    qc.MultipleChoice(
        question="What significant role did Thomas Paine's pamphlet \"Common Sense\" play in the American Revolution?",
        correct_answers=['It galvanized public opinion in favor of independence from Britain.'],
        wrong_answers=['He was a general in the Continental Army', 'He was a leading negotiator of the Treaty of Paris', 'He was the primary author of the Declaration of Independence'],
        explanation="Thomas Paine's \"Common Sense,\" published in 1776, was a powerful argument for American independence and significantly swayed public opinion towards revolution."
    ),
    qc.MultipleChoice(
        question="What did Shay's Rebellion primarily expose?",
        correct_answers=['The weaknesses of the Articles of Confederation government.'],
        wrong_answers=['A British plot to retake the colonies', 'A widespread slave revolt in the South', 'The strength of the national currency'],
        explanation="Shay's Rebellion (1786-1787), an uprising by Massachusetts farmers, highlighted the inability of the government under the Articles of Confederation to maintain order and manage economic problems, significantly influencing the call for a stronger federal government."
    )
])
ap_us_history_sections.append(section_apush_period3)

# Section: Period 4: 1800-1848
section_apush_period4 = Quiz.Section("Period 4: 1800-1848")
section_apush_period4.questions.extend([
    qc.MultipleChoice(
        question="The election of 1800 marked what significant event in American politics?",
        correct_answers=['A peaceful transfer of power between rival political parties.'],
        wrong_answers=['The beginning of the Civil War', 'The end of the Federalist Party as a national force (though this was a gradual process)', 'The impeachment of a president for the first time'],
        explanation="The election of 1800, where Thomas Jefferson (Democratic-Republican) defeated John Adams (Federalist), was significant for being the first peaceful transfer of power from one political party to another in American history."
    ),
    qc.TrueFalseQuestion(
        question="The Louisiana Purchase significantly decreased the geographical size of the United States.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="The Louisiana Purchase in 1803 more than doubled the size of the United States, adding approximately 828,000 square miles."
    ),
    qc.ShortAnswer(
        question="What was the Monroe Doctrine?",
        correct_answer=["A U.S. foreign policy stating that European powers should no longer colonize or interfere with the affairs of nations in the Americas."],
        explanation="The Monroe Doctrine, articulated by President James Monroe in 1823, was a U.S. foreign policy that warned European powers against further colonization or intervention in the newly independent nations of the Western Hemisphere (the Americas).",
        grading_instructions="Answer should mention U.S. opposition to European colonization/interference in the Americas. Be detailed and accurate."
    )
])
ap_us_history_sections.append(section_apush_period4)

# Section: Period 5: 1844-1877
section_apush_period5 = Quiz.Section("Period 5: 1844-1877")
section_apush_period5.questions.extend([
    qc.MultipleChoice(
        question="What belief served as a powerful ideological driver for westward movement and territorial acquisitions in the 19th century United States?",
        correct_answers=['Manifest Destiny'],
        wrong_answers=['Communism', 'Isolationism', 'The American Dream (as a later concept)'],
        explanation="Manifest Destiny was a widely held 19th-century American cultural belief that the United States was destined to expand across the North American continent, from the Atlantic to the Pacific Ocean."
    ),
    qc.TrueFalseQuestion(
        question="The Missouri Compromise of 1820 successfully and permanently resolved the issue of slavery in westward territories and prevented the Civil War.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="The Missouri Compromise temporarily maintained a balance between free and slave states but did not permanently resolve the issue. Later compromises also failed, ultimately leading to the Civil War."
    ),
    qc.ShortAnswer(
        question="Name one major cause of the American Civil War.",
        correct_answer=["Slavery", "States' rights (in the context of slavery)", "Economic differences between North and South", "The election of Abraham Lincoln"],
        explanation="The Civil War erupted from a combination of factors, primarily centered on the issue of slavery, including disputes over states' rights versus federal authority (especially regarding slavery), economic differences, and territorial expansion.",
        grading_instructions="Accept slavery, states' rights, economic differences, or similar primary causes. Be detailed and accurate."
    )
])
ap_us_history_sections.append(section_apush_period5)

# Section: Period 6: 1865-1898
section_apush_period6 = Quiz.Section("Period 6: 1865-1898")
section_apush_period6.questions.extend([
    qc.MultipleChoice(
        question="What was the concept of the \"New South\" that emerged after the Civil War?",
        correct_answers=['An ideology advocating for industrialization and a diversified economy in the South to move away from its agrarian past.'],
        wrong_answers=['A return to the plantation system with reinstated slavery', 'Complete political and social segregation enforced by the North', 'A movement for Southern states to secede again'],
        explanation="The \"New South\" was an idea promoted by some Southerners after the Civil War advocating for the region to diversify its economy, embrace industrialization, and move beyond its reliance on agriculture (particularly cotton) and the plantation system of the \"Old South.\""
    ),
    qc.TrueFalseQuestion(
        question="The U.S. government consistently and honorably upheld treaties made with Native American tribes during the period of westward expansion.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="The U.S. government systematically violated numerous treaties with Native American tribes during westward expansion, often leading to conflict and the forced removal of tribes from their ancestral lands."
    ),
    qc.MultipleChoice(
        question="What did the Populist Party (People's Party) primarily advocate for during the late 19th century?",
        correct_answers=['Government regulation of railroads, land reform, and the free coinage of silver.'],
        wrong_answers=['A strong national bank controlled by private interests', 'High protective tariffs to benefit industrialists', 'Laissez-faire economics with minimal government intervention'],
        explanation="The Populist Party, active in the 1890s, advocated for reforms such as government regulation of railroads and telegraphs, land reform, a graduated income tax, and the unlimited coinage of silver to increase the money supply, aiming to help farmers and laborers."
    ),
    qc.TrueFalseQuestion(
        question="The two major political parties (Democrats and Republicans) during the Gilded Age were widely known for their strong ideological differences and unwavering commitment to addressing critical national policy issues.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="During the Gilded Age, the Democrats and Republicans often differed little on major policy issues and were frequently characterized by political corruption, machine politics, and a focus on patronage rather than substantive reform."
    ),
    qc.ShortAnswer(
        question="What was the \"new immigration\" wave that occurred in the late 19th and early 20th centuries?",
        correct_answer=["A significant influx of immigrants primarily from Southern and Eastern Europe, as well as Asia, to the United States."],
        explanation="The \"new immigration\" wave, from roughly the 1880s to the 1920s, brought large numbers of immigrants to the United States from Southern and Eastern Europe (e.g., Italy, Poland, Russia, Greece) and Asia (e.g., China, Japan), contrasting with earlier waves predominantly from Northern and Western Europe.",
        grading_instructions="Mention immigrants from Southern/Eastern Europe or Asia. Be detailed and accurate."
    )
])
ap_us_history_sections.append(section_apush_period6)

quiz_ap_us_history = Quiz(section_bank=ap_us_history_sections, source_material=source_material_ap_us_history, title="AP US History Challenge")

# --- Quiz: USA Citizen's Test ---
usa_citizens_test_sections = []

# Section: American Government
section_us_gov = Quiz.Section("American Government")
section_us_gov.questions.extend([
    qc.MultipleChoice(
        question="What is the supreme law of the land in the United States?",
        correct_answers=['The Constitution'],
        wrong_answers=['The Articles of Confederation', 'The Bill of Rights', 'The Declaration of Independence'],
        explanation="The U.S. Constitution is the foundation and supreme law of the United States."
    ),
    qc.TrueFalseQuestion(
        question="The U.S. Constitution establishes the government, defines its powers, and protects the basic rights of its citizens.",
        correct_answers=['True'],
        wrong_answers=['False'],
        explanation="The Constitution outlines the structure and functions of the U.S. government (separation of powers, checks and balances) and, particularly through the Bill of Rights and subsequent amendments, safeguards the fundamental rights of individuals."
    ),
    qc.ShortAnswer(
        question="What is meant by the phrase 'We the People' at the beginning of the U.S. Constitution?",
        correct_answer=["It signifies that the power of the government comes from the citizens of the United States.", "Self-government", "Popular sovereignty"],
        explanation="'We the People' signifies that the people themselves are the source of the government's authority, underscoring the democratic principle of popular sovereignty in the U.S. system.",
        grading_instructions="Answer should convey the idea of popular sovereignty or that the government's power derives from the citizens. Be detailed and accurate."
    ),
    qc.MultipleChoice(
        question="What is the economic system in the United States?",
        correct_answers=['Capitalist economy', 'Market economy'], # Updated to be more aligned with common civics test answers
        wrong_answers=['Communist economy', 'Socialist economy', 'Barter economy'],
        explanation="The economic system in the United States is primarily a capitalist or market economy, where private individuals and businesses make most economic decisions."
    ),
    qc.TrueFalseQuestion(
        question="The 'Rule of Law' dictates that everyone, including leaders and government officials, must obey the law.",
        correct_answers=['True'],
        wrong_answers=['False'],
        explanation="The 'Rule of Law' is a central principle that no one is above the law; everyone, including government officials and leaders, is subject to and accountable under the law."
    ),
    qc.ShortAnswer(
        question="Name one branch or part of the U.S. government.",
        correct_answer=["Legislative", "Executive", "Judicial", "Congress", "President", "Courts"],
        explanation="The U.S. government is divided into three branches: Legislative (Congress), Executive (President), and Judicial (Courts).",
        grading_instructions="Accept any one of the three branches or their main components. Be detailed and accurate."
    ),
    qc.MultipleChoice(
        question="What stops one branch of government from becoming too powerful?",
        correct_answers=['Checks and balances', 'Separation of powers'],
        wrong_answers=['Direct democracy', 'Federalism', 'The President alone'],
        explanation="The system of checks and balances, along with the separation of powers, ensures that no single branch of government (legislative, executive, judicial) accumulates excessive authority."
    ),
    qc.MultipleChoice(
        question="How many U.S. Senators are there?",
        correct_answers=['100'],
        wrong_answers=['50', '435', '200'],
        explanation="There are 100 U.S. Senators, with two elected from each of the 50 states."
    ),
    qc.MultipleChoice(
        question="We elect a U.S. Representative for how many years?",
        correct_answers=['Two'],
        wrong_answers=['Four', 'Six', 'Eight'],
        explanation="U.S. Representatives are elected for a term of two years."
    )
])
usa_citizens_test_sections.append(section_us_gov)

# Section: American History
section_us_history = Quiz.Section("American History")
section_us_history.questions.extend([
    qc.MultipleChoice(
        question="What war was fought by the American colonists for U.S. independence from Great Britain?",
        correct_answers=['The Revolutionary War', 'The American Revolution'],
        wrong_answers=['The Civil War', 'World War I', 'The French and Indian War'],
        explanation="The American Revolution (or Revolutionary War) was fought from 1775 to 1783, resulting in the independence of the United States from British rule."
    ),
    qc.TrueFalseQuestion(
        question="Thomas Jefferson was the primary author of the Declaration of Independence.",
        correct_answers=['True'],
        wrong_answers=['False'],
        explanation="Thomas Jefferson is credited as the principal author of the Declaration of Independence, a foundational document in American history adopted on July 4, 1776."
    ),
    qc.ShortAnswer(
        question="Name one reason why the colonists fought the British.",
        correct_answer=["High taxes (taxation without representation)", "British army stayed in their houses (quartering)", "They didn't have self-government", "Boston Massacre", "Intolerable Acts"],
        explanation="The colonists fought for independence due to grievances such as high taxes (e.g., Stamp Act, Tea Act) without representation in the British Parliament, restrictions on trade, quartering of British soldiers, and a desire for self-government.",
        grading_instructions="Accept reasons like 'taxation without representation,' 'no self-government,' or specific acts/events. Be detailed and accurate."
    ),
    qc.MultipleChoice(
        question="Who was the President of the United States during the Civil War?",
        correct_answers=['Abraham Lincoln'],
        wrong_answers=['Andrew Jackson', 'George Washington', 'Thomas Jefferson'],
        explanation="Abraham Lincoln was the 16th President of the United States, serving from March 1861 until his assassination in April 1865. He led the country through the Civil War and worked to preserve the Union."
    ),
    qc.TrueFalseQuestion(
        question="The Civil War was fought between the North (Union) and the South (Confederacy) primarily over the issue of states' rights, with slavery being a minor factor.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="The Civil War's primary cause was slavery, including its expansion into western territories. While states' rights were invoked, it was largely in the context of protecting the institution of slavery."
    ),
    qc.ShortAnswer(
        question="What did the Emancipation Proclamation do?",
        correct_answer=["Freed slaves in the Confederate states", "Freed slaves in the Confederacy", "Freed slaves in most Southern states"],
        explanation="Issued by Abraham Lincoln in 1863, the Emancipation Proclamation declared slaves in the Confederate-held territory to be free. It was a crucial step towards the abolition of slavery in the United States.",
        grading_instructions="Answer should state it freed slaves in Confederate states/territory. Be detailed and accurate."
    ),
    qc.MultipleChoice(
        question="What movement tried to end racial discrimination in the United States, particularly in the mid-20th century?",
        correct_answers=['Civil Rights Movement'],
        wrong_answers=['Abolitionist Movement (19th century)', 'Temperance Movement', "Women's Suffrage Movement"],
        explanation="The Civil Rights Movement, especially prominent in the 1950s and 1960s, fought to end racial segregation and discrimination against African Americans and to secure legal recognition and federal protection of the citizenship rights enumerated in the Constitution and federal law."
    ),
    qc.ShortAnswer(
        question="Who is often called the 'Father of Our Country'?",
        correct_answer=["George Washington"],
        explanation="George Washington is known as the 'Father of Our Country' for his leadership as commander-in-chief of the Continental Army during the American Revolution and his role as the first president of the United States.",
        grading_instructions="Answer must be George Washington. Be detailed and accurate."
    ),
    qc.ShortAnswer(
        question="Name one war fought by the United States in the 1900s.",
        correct_answer=["World War I", "World War II", "Korean War", "Vietnam War", "Persian Gulf War"],
        explanation="The United States fought in several major wars in the 1900s (20th century), including World War I, World War II, the Korean War, the Vietnam War, and the (Persian) Gulf War.",
        grading_instructions="Accept any of the listed major conflicts from the 20th century. Be detailed and accurate."
    )
])
usa_citizens_test_sections.append(section_us_history)

# Section: Integrated Civics
section_us_civics = Quiz.Section("Integrated Civics (Symbols and Holidays)")
section_us_civics.questions.extend([
    qc.MultipleChoice(
        question="What is the capital of the United States?",
        correct_answers=['Washington, D.C.'],
        wrong_answers=['New York City', 'Philadelphia', 'Boston'],
        explanation="Washington, D.C. (District of Columbia) is the capital of the United States."
    ),
    qc.TrueFalseQuestion(
        question="The Statue of Liberty is located in Boston Harbor.",
        correct_answers=['False'],
        wrong_answers=['True'],
        explanation="The Statue of Liberty is located on Liberty Island in New York Harbor."
    ),
    qc.ShortAnswer(
        question="How many stripes are on the U.S. flag?",
        correct_answer=["13", "Thirteen"],
        explanation="The U.S. flag has 13 stripes, representing the 13 original colonies that declared independence from Great Britain.",
        grading_instructions="Answer should be 13. Be detailed and accurate."
    ),
    qc.MultipleChoice(
        question="What do the stars on the U.S. flag represent?",
        correct_answers=['The 50 states'],
        wrong_answers=['The 13 original colonies', 'The branches of government', 'The signers of the Declaration of Independence'],
        explanation="The 50 stars on the U.S. flag represent the 50 states of the United States."
    ),
    qc.TrueFalseQuestion(
        question="Independence Day in the United States is celebrated on July 4th.",
        correct_answers=['True'],
        wrong_answers=['False'],
        explanation="Independence Day, commemorating the adoption of the Declaration of Independence on July 4, 1776, is celebrated annually on July 4th."
    ),
    qc.ShortAnswer(
        question="What is one right or freedom from the First Amendment to the Constitution?",
        correct_answer=["Speech", "Religion", "Assembly", "Press", "Petition the government"],
        explanation="The First Amendment guarantees several fundamental rights and freedoms, including freedom of speech, freedom of religion, freedom of the press, freedom of assembly, and the right to petition the government.",
        grading_instructions="Accept any one of the five freedoms listed. Be detailed and accurate."
    ),
    qc.MultipleChoice(
        question="Which U.S. federal holiday, observed in November, celebrates all people who have served in the U.S. military?",
        correct_answers=['Veterans Day'],
        wrong_answers=['Independence Day', 'Labor Day', 'Memorial Day'],
        explanation="Veterans Day, observed annually on November 11th, honors all individuals who have served in the U.S. armed forces."
    ),
    qc.TrueFalseQuestion(
        question="The U.S. motto 'E Pluribus Unum' means 'From one, many.'",
        correct_answers=['False'], # It means "Out of many, one"
        wrong_answers=['True'],
        explanation="'E Pluribus Unum' is a Latin phrase meaning 'Out of many, one.' It reflects the idea that a single nation was formed from many states or peoples."
    ),
    qc.MultipleChoice(
        question="When do we celebrate Independence Day?",
        correct_answers=['July 4'],
        wrong_answers=['December 25', 'January 1', 'The first Monday in September'],
        explanation="Independence Day is celebrated on July 4th each year."
    )
])
usa_citizens_test_sections.append(section_us_civics)

quiz_usa_citizens_test = Quiz(section_bank=usa_citizens_test_sections, source_material=source_material_usa_citizens_test, title="US Citizenship Test Practice")

# List of all premade quizzes available
all_premade_quizzes = [quiz_traffic_laws, quiz_ap_us_history, quiz_usa_citizens_test]

# Optional: If your application dynamically loads quizzes by name,
# you might want a dictionary for easy lookup:
# premade_quiz_map = {
# "california_driving": quiz_traffic_laws,
# "ap_us_history": quiz_ap_us_history,
# "us_citizenship_test": quiz_usa_citizens_test,
# }