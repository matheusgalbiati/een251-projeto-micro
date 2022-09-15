import asyncio
import io
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, QualityForRecognition


# This key will serve all examples in this document.
KEY = "2c0a6ae783374aca99fe12e1e32d3250"

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = "https://projeto-een251.cognitiveservices.azure.com/"

# Base url for the Verify and Facelist/Large Facelist operations
IMAGE_BASE_URL = 'Images/'

# Used in the Person Group Operations and Delete Person Group examples.
# You can call list_person_groups to print a list of preexisting PersonGroups.
# SOURCE_PERSON_GROUP_ID should be all lowercase and alphanumeric. For example, 'mygroupname' (dashes are OK).
PERSON_GROUP_ID = str(uuid.uuid4()) # assign a random ID (or name it anything)

# Used for the Delete Person Group example.
TARGET_PERSON_GROUP_ID = str(uuid.uuid4()) # assign a random ID (or name it anything)

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
face_client.person_group.create()
'''
Create the PersonGroup
'''
# Create empty Person Group. Person Group ID must be lower case, alphanumeric, and/or with '-', '_'.
print('Person group:', PERSON_GROUP_ID)
face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID, recognition_model='recognition_03')

# Define woman friend
matheus = face_client.person_group_person.create(PERSON_GROUP_ID, name="Matheus")
# Define man friend
fernando = face_client.person_group_person.create(PERSON_GROUP_ID, name="Fernando")
# Define child friend
# child = face_client.person_group_person.create(PERSON_GROUP_ID, name="Child")

'''
Detect faces and register them to each person
'''
# Find all jpeg images of friends in working directory (TBD pull from web instead)
matheus_images = ["Images/matheus1.jpg", "Images/matheus2.jpg", "Images/matheus3.jpg"]
fernando_images = ["Images/fernando1.jpg", "Images/fernando2.jpg", "Images/fernando3.jpg"]
# child_images = ["https://csdx.blob.core.windows.net/resources/Face/Images/Family1-Son1.jpg", "https://csdx.blob.core.windows.net/resources/Face/Images/Family1-Son2.jpg"]

# Add to matheus person
for image in matheus_images:
    # Check if the image is of sufficent quality for recognition.
    # sufficientQuality = True
    detected_faces = face_client.face.detect_with_stream(image=image, detection_model='detection_03', recognition_model='recognition_03')
    for face in detected_faces:
        # if face.face_attributes.quality_for_recognition != QualityForRecognition.high:
        #     sufficientQuality = False
        #     break
        face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, matheus.person_id, image)
        print("face {} added to person {}".format(face.face_id, matheus.person_id))

    # if not sufficientQuality: continue

# Add to fernando person
for image in fernando_images:
    # Check if the image is of sufficent quality for recognition.
    # sufficientQuality = True
    detected_faces = face_client.face.detect_with_stream(image=image, detection_model='detection_03', recognition_model='recognition_03')
    for face in detected_faces:
        # if face.face_attributes.quality_for_recognition != QualityForRecognition.high:
        #     sufficientQuality = False
        #     break
        face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, fernando.person_id, image)
        print("face {} added to person {}".format(face.face_id, fernando.person_id))

    # if not sufficientQuality: continue

# # Add to child person
# for image in child_images:
#     # Check if the image is of sufficent quality for recognition.
#     sufficientQuality = True
#     detected_faces = face_client.face.detect_with_url(url=image, detection_model='detection_03', recognition_model='recognition_04', return_face_attributes=['qualityForRecognition'])
#     for face in detected_faces:
#         if face.face_attributes.quality_for_recognition != QualityForRecognition.high:
#             sufficientQuality = False
#             print("{} has insufficient quality".format(face))
#             break
#         face_client.person_group_person.add_face_from_url(PERSON_GROUP_ID, child.person_id, image)
#         print("face {} added to person {}".format(face.face_id, child.person_id))
#     if not sufficientQuality: continue


'''
Train PersonGroup
'''
# Train the person group
print("pg resource is {}".format(PERSON_GROUP_ID))
rawresponse = face_client.person_group.train(PERSON_GROUP_ID, raw= True)
print(rawresponse)

while (True):
    training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
    print("Training status: {}.".format(training_status.status))
    print()
    if (training_status.status is TrainingStatusType.succeeded):
        break
    elif (training_status.status is TrainingStatusType.failed):
        face_client.person_group.delete(person_group_id=PERSON_GROUP_ID)
        sys.exit('Training the person group has failed.')
    time.sleep(5)

'''
Identify a face against a defined PersonGroup
'''
# Group image for testing against
test_image = "Tests/teste_matheus.jpg"

print('Pausing for 10 seconds to avoid triggering rate limit on free account...')
time.sleep (10)

# Detect faces
face_ids = []
# We use detection model 3 to get better performance, recognition model 4 to support quality for recognition attribute.
faces = face_client.face.detect_with_stream(test_image, detection_model='detection_03', recognition_model='recognition_03')
for face in faces:
    # Only take the face if it is of sufficient quality.
    # if face.face_attributes.quality_for_recognition == QualityForRecognition.high or face.face_attributes.quality_for_recognition == QualityForRecognition.medium:
    #     face_ids.append(face.face_id)
    face_ids.append(face.face_id)

# Identify faces
results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
print('Identifying faces in image')
if not results:
    print('No person identified in the person group')
for person in results:
    if len(person.candidates) > 0:
        print('Person for face ID {} is identified in image, with a confidence of {}.'.format(person.face_id, person.candidates[0].confidence)) # Get topmost confidence score
    else:
        print('No person identified for face ID {} in image.'.format(person.face_id))

print()
print('End of quickstart.')