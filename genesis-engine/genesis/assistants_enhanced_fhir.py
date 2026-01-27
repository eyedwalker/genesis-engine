"""
Enhanced FHIR Compliance Reviewer

Comprehensive FHIR healthcare interoperability covering:
- FHIR R4/R5 resources and differences
- SMART on FHIR authorization
- CDS Hooks integration
- US Core and IPA profiles
- Terminology services (ValueSet, CodeSystem)
- FHIR search parameters
- Bulk data export ($export)
- Subscriptions

References:
- HL7 FHIR: https://hl7.org/fhir/
- SMART on FHIR: https://docs.smarthealthit.org/
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class FHIRFinding(BaseModel):
    finding_id: str = Field(...)
    title: str = Field(...)
    severity: str = Field(...)
    category: str = Field(...)
    fhir_resource: str = Field(default="")
    profile_violated: str = Field(default="")
    current_implementation: str = Field(default="")
    compliant_implementation: str = Field(default="")
    tools: List[Dict[str, str]] = Field(default_factory=list)
    remediation: Dict[str, str] = Field(default_factory=dict)


class EnhancedFHIRAssistant:
    """Enhanced FHIR Compliance Reviewer"""

    def __init__(self):
        self.name = "Enhanced FHIR Compliance Reviewer"
        self.version = "2.0.0"
        self.standards = ["FHIR R4", "FHIR R5", "US Core", "SMART on FHIR"]

    @staticmethod
    def fhir_resources() -> Dict[str, Any]:
        """Core FHIR resources"""
        return {
            "patient": """
// Patient resource (US Core Profile)
{
  "resourceType": "Patient",
  "id": "example",
  "meta": {
    "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
  },
  "identifier": [{
    "system": "http://hospital.org/patients",
    "value": "12345"
  }],
  "name": [{
    "family": "Smith",
    "given": ["John", "Michael"]
  }],
  "gender": "male",
  "birthDate": "1990-01-15",
  "address": [{
    "line": ["123 Main St"],
    "city": "Boston",
    "state": "MA",
    "postalCode": "02101"
  }]
}
            """,
            "observation": """
// Observation (vital signs)
{
  "resourceType": "Observation",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/observation-category",
      "code": "vital-signs"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "85354-9",
      "display": "Blood pressure panel"
    }]
  },
  "subject": {
    "reference": "Patient/example"
  },
  "effectiveDateTime": "2024-01-15T10:30:00Z",
  "component": [
    {
      "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
      "valueQuantity": {"value": 120, "unit": "mmHg"}
    },
    {
      "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4"}]},
      "valueQuantity": {"value": 80, "unit": "mmHg"}
    }
  ]
}
            """,
        }

    @staticmethod
    def smart_on_fhir() -> Dict[str, Any]:
        """SMART on FHIR authorization"""
        return {
            "scopes": """
# SMART Scopes
patient/*.read      # Read any resource for current patient
patient/Observation.read  # Read observations for current patient
user/*.read         # Read any resource user has access to
launch/patient      # Request patient context at launch
openid fhirUser     # Get user identity claims
offline_access      # Request refresh token
            """,
            "launch": """
# EHR Launch Flow
1. EHR redirects to app: GET /authorize?
     response_type=code&
     client_id=my_app&
     redirect_uri=https://myapp.com/callback&
     scope=launch patient/*.read&
     state=abc123&
     aud=https://fhir.hospital.org/r4

2. User authenticates with EHR

3. EHR redirects back: https://myapp.com/callback?
     code=xyz789&
     state=abc123

4. App exchanges code for token: POST /token
     grant_type=authorization_code&
     code=xyz789&
     redirect_uri=https://myapp.com/callback

5. Response includes:
   {
     "access_token": "eyJ...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "scope": "launch patient/*.read",
     "patient": "12345"  // Patient context
   }
            """,
        }

    @staticmethod
    def cds_hooks() -> Dict[str, Any]:
        """CDS Hooks integration"""
        return {
            "hook_types": [
                "patient-view - When patient chart opened",
                "order-select - When order selected",
                "order-sign - Before signing order",
                "appointment-book - When scheduling",
            ],
            "example": """
// CDS Hook Request (patient-view)
{
  "hookInstance": "abc-123",
  "hook": "patient-view",
  "context": {
    "userId": "Practitioner/123",
    "patientId": "Patient/456"
  },
  "prefetch": {
    "patient": {"resourceType": "Patient", "id": "456"}
  }
}

// CDS Hook Response (card)
{
  "cards": [{
    "uuid": "card-1",
    "summary": "Drug Interaction Alert",
    "indicator": "warning",
    "detail": "Patient is on warfarin. Consider INR monitoring.",
    "source": {"label": "Drug Interaction Service"},
    "suggestions": [{
      "label": "Order INR",
      "actions": [{
        "type": "create",
        "resource": {
          "resourceType": "ServiceRequest",
          "code": {"coding": [{"code": "INR"}]}
        }
      }]
    }]
  }]
}
            """,
        }

    @staticmethod
    def bulk_data() -> Dict[str, Any]:
        """FHIR Bulk Data Export"""
        return {
            "export": """
# Initiate bulk export
GET https://fhir.hospital.org/r4/$export
Accept: application/fhir+json
Prefer: respond-async

# Response: 202 Accepted
Content-Location: https://fhir.hospital.org/r4/bulkstatus/job123

# Poll for status
GET https://fhir.hospital.org/r4/bulkstatus/job123

# When complete: 200 OK
{
  "transactionTime": "2024-01-15T10:00:00Z",
  "output": [
    {"type": "Patient", "url": "https://storage/patients.ndjson"},
    {"type": "Observation", "url": "https://storage/observations.ndjson"}
  ]
}
            """,
        }

    # =========================================================================
    # US CORE PROFILES
    # =========================================================================

    @staticmethod
    def us_core_profiles() -> Dict[str, Any]:
        """US Core Implementation Guide profiles"""
        return {
            "overview": {
                "description": "US Core defines minimum required data elements for US healthcare",
                "version": "US Core 6.0.0 (based on FHIR R4)",
                "required_profiles": [
                    "US Core Patient",
                    "US Core Practitioner",
                    "US Core Organization",
                    "US Core Encounter",
                    "US Core Condition",
                    "US Core Procedure",
                    "US Core Observation",
                    "US Core Medication Request",
                    "US Core Allergy Intolerance",
                    "US Core Immunization",
                    "US Core Diagnostic Report",
                    "US Core Document Reference",
                    "US Core Care Plan",
                ],
            },
            "us_core_patient": '''
// US Core Patient - Required elements
{
  "resourceType": "Patient",
  "id": "example",
  "meta": {
    "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
  },
  // REQUIRED: identifier (usually MRN)
  "identifier": [{
    "system": "http://hospital.example.org/patients",
    "value": "12345"
  }],
  // REQUIRED: name
  "name": [{
    "family": "Smith",  // Required
    "given": ["John"]   // Required
  }],
  // REQUIRED: gender
  "gender": "male",
  // REQUIRED (if known): birthDate
  "birthDate": "1990-01-15",
  // US Core extensions
  "extension": [
    {
      "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
      "extension": [
        {
          "url": "ombCategory",
          "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2106-3",
            "display": "White"
          }
        },
        {
          "url": "text",
          "valueString": "White"
        }
      ]
    },
    {
      "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
      "extension": [
        {
          "url": "ombCategory",
          "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2186-5",
            "display": "Not Hispanic or Latino"
          }
        }
      ]
    },
    {
      "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
      "valueCode": "M"
    }
  ]
}
            ''',
            "us_core_vital_signs": '''
// US Core Vital Signs - Blood Pressure
{
  "resourceType": "Observation",
  "meta": {
    "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure"]
  },
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/observation-category",
      "code": "vital-signs",
      "display": "Vital Signs"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "85354-9",
      "display": "Blood pressure panel"
    }]
  },
  "subject": {
    "reference": "Patient/example"
  },
  "effectiveDateTime": "2024-01-15T10:30:00Z",
  "component": [
    {
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "8480-6",
          "display": "Systolic blood pressure"
        }]
      },
      "valueQuantity": {
        "value": 120,
        "unit": "mmHg",
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]"
      }
    },
    {
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "8462-4",
          "display": "Diastolic blood pressure"
        }]
      },
      "valueQuantity": {
        "value": 80,
        "unit": "mmHg",
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]"
      }
    }
  ]
}
            ''',
        }

    # =========================================================================
    # FHIR SEARCH
    # =========================================================================

    @staticmethod
    def fhir_search() -> Dict[str, Any]:
        """FHIR Search parameters and patterns"""
        return {
            "basic_search": '''
# Basic search patterns

# Search by patient ID
GET /Patient/12345

# Search patients by name
GET /Patient?name=smith

# Search with multiple parameters (AND)
GET /Patient?name=john&birthdate=1990-01-15

# Search with OR (using comma)
GET /Patient?name=smith,jones

# Search by date range
GET /Observation?date=ge2024-01-01&date=le2024-12-31

# Search with modifiers
GET /Patient?name:exact=Smith       # Exact match
GET /Patient?name:contains=smi      # Contains
GET /Patient?birthdate:missing=true # Missing values

# Include related resources
GET /Patient?_include=Patient:organization

# Reverse include
GET /Patient?_revinclude=Observation:patient

# Sort results
GET /Observation?_sort=-date        # Descending
GET /Observation?_sort=date,patient # Multiple

# Pagination
GET /Patient?_count=20&_offset=40
            ''',
            "chained_search": '''
# Chained search - search on referenced resource properties

# Find observations for patients named "Smith"
GET /Observation?patient.name=smith

# Find encounters at organization named "General Hospital"
GET /Encounter?serviceProvider.name=General%20Hospital

# Multiple chained parameters
GET /Observation?patient.name=smith&patient.birthdate=1990-01-15
            ''',
            "composite_search": '''
# Composite search parameters

# Observation with specific code AND value
GET /Observation?component-code-value-quantity=8480-6$120|http://unitsofmeasure.org|mm[Hg]

# Search by token (system|code)
GET /Observation?code=http://loinc.org|85354-9
            ''',
            "python_client": '''
# Python FHIR client with search
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.observation import Observation

class FHIRSearchService:
    def __init__(self, base_url: str, access_token: str):
        settings = {
            'app_id': 'my_app',
            'api_base': base_url
        }
        self.smart = client.FHIRClient(settings=settings)
        self.smart.server.session.headers['Authorization'] = f'Bearer {access_token}'

    def search_patients(self, name: str = None, birthdate: str = None) -> list[Patient]:
        """Search patients with parameters"""
        search_params = {}
        if name:
            search_params['name'] = name
        if birthdate:
            search_params['birthdate'] = birthdate

        search = Patient.where(struct=search_params)
        patients = search.perform_resources(self.smart.server)
        return patients

    def get_patient_observations(
        self,
        patient_id: str,
        code: str = None,
        date_from: str = None,
        date_to: str = None
    ) -> list[Observation]:
        """Get observations for a patient"""
        search_params = {
            'patient': patient_id,
            '_sort': '-date'
        }

        if code:
            search_params['code'] = code

        if date_from:
            search_params['date'] = [f'ge{date_from}']
        if date_to:
            if 'date' not in search_params:
                search_params['date'] = []
            search_params['date'].append(f'le{date_to}')

        search = Observation.where(struct=search_params)
        return search.perform_resources(self.smart.server)

    def search_with_pagination(self, resource_type: str, params: dict, page_size: int = 50):
        """Search with pagination handling"""
        params['_count'] = page_size
        all_results = []
        offset = 0

        while True:
            params['_offset'] = offset
            bundle = self.smart.server.request_json(
                f'{resource_type}?{urlencode(params, doseq=True)}'
            )

            entries = bundle.get('entry', [])
            if not entries:
                break

            all_results.extend([e['resource'] for e in entries])

            # Check for more pages
            next_link = next(
                (l for l in bundle.get('link', []) if l['relation'] == 'next'),
                None
            )
            if not next_link:
                break

            offset += page_size

        return all_results
            ''',
        }

    # =========================================================================
    # FHIR OPERATIONS
    # =========================================================================

    @staticmethod
    def fhir_operations() -> Dict[str, Any]:
        """FHIR Operations ($operation)"""
        return {
            "everything": '''
# $everything - Get all data for a patient
GET /Patient/12345/$everything

# Response: Bundle with all patient data
{
  "resourceType": "Bundle",
  "type": "searchset",
  "entry": [
    {"resource": {"resourceType": "Patient", ...}},
    {"resource": {"resourceType": "Condition", ...}},
    {"resource": {"resourceType": "Observation", ...}},
    {"resource": {"resourceType": "MedicationRequest", ...}}
  ]
}

# With date range
GET /Patient/12345/$everything?start=2024-01-01&end=2024-12-31
            ''',
            "validate": '''
# $validate - Validate a resource against a profile
POST /Patient/$validate
Content-Type: application/fhir+json

{
  "resourceType": "Parameters",
  "parameter": [
    {
      "name": "resource",
      "resource": {
        "resourceType": "Patient",
        "name": [{"family": "Smith"}]
        // Missing required fields...
      }
    },
    {
      "name": "profile",
      "valueUri": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
    }
  ]
}

# Response: OperationOutcome with validation errors
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "required",
      "details": {"text": "Patient.identifier: minimum required = 1, but only found 0"},
      "location": ["Patient.identifier"]
    },
    {
      "severity": "error",
      "code": "required",
      "details": {"text": "Patient.gender: minimum required = 1, but only found 0"},
      "location": ["Patient.gender"]
    }
  ]
}
            ''',
            "convert": '''
# $convert - Convert between formats
POST /$convert
Content-Type: application/fhir+xml
Accept: application/fhir+json

<Patient xmlns="http://hl7.org/fhir">
  <name>
    <family value="Smith"/>
  </name>
</Patient>

# Response: JSON format
{
  "resourceType": "Patient",
  "name": [{"family": "Smith"}]
}
            ''',
            "match": '''
# $match - Patient matching
POST /Patient/$match
Content-Type: application/fhir+json

{
  "resourceType": "Parameters",
  "parameter": [
    {
      "name": "resource",
      "resource": {
        "resourceType": "Patient",
        "name": [{"family": "Smith", "given": ["John"]}],
        "birthDate": "1990-01-15"
      }
    },
    {
      "name": "onlyCertainMatches",
      "valueBoolean": false
    }
  ]
}

# Response: Bundle with matching patients and match scores
{
  "resourceType": "Bundle",
  "entry": [
    {
      "resource": {"resourceType": "Patient", "id": "123", ...},
      "search": {
        "score": 0.95,
        "extension": [{
          "url": "http://hl7.org/fhir/StructureDefinition/match-grade",
          "valueCode": "certain"
        }]
      }
    }
  ]
}
            ''',
        }

    # =========================================================================
    # FHIR SUBSCRIPTIONS
    # =========================================================================

    @staticmethod
    def fhir_subscriptions() -> Dict[str, Any]:
        """FHIR Subscription patterns (R4 and R5)"""
        return {
            "r4_subscription": '''
// R4 Subscription (webhooks)
{
  "resourceType": "Subscription",
  "status": "requested",
  "reason": "Monitor new patients",
  "criteria": "Patient?_lastUpdated=gt2024-01-01",
  "channel": {
    "type": "rest-hook",
    "endpoint": "https://myapp.example.com/fhir-webhook",
    "payload": "application/fhir+json",
    "header": [
      "Authorization: Bearer ${webhook_token}"
    ]
  }
}

// Server sends POST to endpoint when criteria matches
POST https://myapp.example.com/fhir-webhook
Content-Type: application/fhir+json

{
  "resourceType": "Patient",
  "id": "new-patient-123",
  ...
}
            ''',
            "r5_subscriptions_topic": '''
// R5 Subscriptions with Topics (more powerful)

// 1. Server defines SubscriptionTopic
{
  "resourceType": "SubscriptionTopic",
  "url": "http://example.org/SubscriptionTopic/patient-admission",
  "title": "Patient Admission",
  "status": "active",
  "resourceTrigger": [{
    "resource": "Encounter",
    "supportedInteraction": ["create", "update"],
    "queryCriteria": {
      "previous": "status:not=in-progress",
      "resultForCreate": "test-passes",
      "current": "status=in-progress",
      "resultForDelete": "test-fails"
    }
  }],
  "eventTrigger": [{
    "description": "Patient admitted to hospital",
    "event": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v2-0003",
        "code": "A01"
      }]
    }
  }],
  "canFilterBy": [
    {"resource": "Encounter", "filterParameter": "patient"},
    {"resource": "Encounter", "filterParameter": "location"}
  ],
  "notificationShape": [{
    "resource": "Encounter",
    "include": ["Encounter:patient", "Encounter:location"]
  }]
}

// 2. Client creates Subscription to Topic
{
  "resourceType": "Subscription",
  "status": "requested",
  "topic": "http://example.org/SubscriptionTopic/patient-admission",
  "filterBy": [{
    "resourceType": "Encounter",
    "filterParameter": "location",
    "value": "Location/icu"
  }],
  "channelType": {
    "system": "http://terminology.hl7.org/CodeSystem/subscription-channel-type",
    "code": "rest-hook"
  },
  "endpoint": "https://myapp.example.com/admission-webhook",
  "heartbeatPeriod": 60,
  "content": "full-resource"
}
            ''',
            "websocket_subscription": '''
// WebSocket subscription for real-time updates

// Create subscription with websocket channel
{
  "resourceType": "Subscription",
  "status": "requested",
  "criteria": "Observation?patient=Patient/123&category=vital-signs",
  "channel": {
    "type": "websocket"
  }
}

// Server responds with subscription ID
{
  "resourceType": "Subscription",
  "id": "sub-123",
  "status": "active",
  ...
}

// Client connects to WebSocket
// wss://fhir.hospital.org/websocket/sub-123

// Python client example
import websockets
import asyncio

async def subscribe_to_vitals(patient_id: str):
    uri = f"wss://fhir.hospital.org/websocket/{subscription_id}"

    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            observation = json.loads(message)

            # Process vital sign update
            process_vital_sign(observation)

            # Send acknowledgment
            await websocket.send(json.dumps({"ack": observation["id"]}))
            ''',
        }

    # =========================================================================
    # FHIR MAPPING
    # =========================================================================

    @staticmethod
    def fhir_mapping() -> Dict[str, Any]:
        """FHIR data mapping patterns"""
        return {
            "hl7v2_to_fhir": '''
# HL7 v2 to FHIR mapping example
# ADT^A01 (Admit) to FHIR Encounter

# Input: HL7 v2 ADT^A01
MSH|^~\&|HIS|HOSPITAL|FHIR|CONVERTER|20240115120000||ADT^A01|MSG001|P|2.5
PID|1||12345^^^MRN||Smith^John^Michael||19900115|M
PV1|1|I|ICU^101^A|E||||||DOC123^Jones^Mary|||||||V123

# Output: FHIR Encounter
from hl7apy.parser import parse_message

class HL7v2ToFHIR:
    def convert_adt_a01(self, message: str) -> dict:
        """Convert ADT^A01 to FHIR Encounter"""
        msg = parse_message(message)

        # Extract segments
        pid = msg.pid
        pv1 = msg.pv1

        # Build FHIR Patient
        patient = {
            "resourceType": "Patient",
            "identifier": [{
                "system": "http://hospital.org/mrn",
                "value": str(pid.pid_3.pid_3_1)  # MRN
            }],
            "name": [{
                "family": str(pid.pid_5.pid_5_1),  # Last name
                "given": [str(pid.pid_5.pid_5_2)]  # First name
            }],
            "gender": "male" if str(pid.pid_8) == "M" else "female",
            "birthDate": self._convert_date(str(pid.pid_7))
        }

        # Build FHIR Encounter
        encounter = {
            "resourceType": "Encounter",
            "status": "in-progress",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "IMP" if str(pv1.pv1_2) == "I" else "AMB",
                "display": "inpatient" if str(pv1.pv1_2) == "I" else "ambulatory"
            },
            "subject": {
                "reference": f"Patient/{patient['identifier'][0]['value']}"
            },
            "location": [{
                "location": {
                    "display": f"{pv1.pv1_3.pv1_3_1}^{pv1.pv1_3.pv1_3_2}"
                }
            }],
            "participant": [{
                "individual": {
                    "identifier": {
                        "value": str(pv1.pv1_7.pv1_7_1)
                    },
                    "display": f"Dr. {pv1.pv1_7.pv1_7_2} {pv1.pv1_7.pv1_7_3}"
                }
            }]
        }

        return {"patient": patient, "encounter": encounter}

    def _convert_date(self, hl7_date: str) -> str:
        """Convert HL7 date (YYYYMMDD) to FHIR date (YYYY-MM-DD)"""
        return f"{hl7_date[:4]}-{hl7_date[4:6]}-{hl7_date[6:8]}"
            ''',
            "ccda_to_fhir": '''
# C-CDA to FHIR conversion
# Use FHIR ConceptMap for terminology mapping

from lxml import etree

class CCDAToFHIR:
    """Convert C-CDA documents to FHIR resources"""

    NAMESPACES = {
        'cda': 'urn:hl7-org:v3',
        'sdtc': 'urn:hl7-org:sdtc'
    }

    def convert_patient(self, ccda_doc: str) -> dict:
        """Extract Patient from C-CDA"""
        root = etree.fromstring(ccda_doc.encode())

        # Navigate to patient element
        patient_role = root.find('.//cda:patientRole', self.NAMESPACES)
        patient = patient_role.find('cda:patient', self.NAMESPACES)

        # Extract identifiers
        ids = patient_role.findall('cda:id', self.NAMESPACES)
        identifiers = []
        for id_elem in ids:
            identifiers.append({
                "system": id_elem.get('root'),
                "value": id_elem.get('extension')
            })

        # Extract name
        name = patient.find('cda:name', self.NAMESPACES)
        given_names = [g.text for g in name.findall('cda:given', self.NAMESPACES)]
        family_name = name.find('cda:family', self.NAMESPACES).text

        # Extract gender
        gender_elem = patient.find('cda:administrativeGenderCode', self.NAMESPACES)
        gender_code = gender_elem.get('code')
        gender_map = {'M': 'male', 'F': 'female', 'UN': 'unknown'}
        gender = gender_map.get(gender_code, 'unknown')

        # Extract birth date
        birth_elem = patient.find('cda:birthTime', self.NAMESPACES)
        birth_date = self._parse_ccda_date(birth_elem.get('value'))

        return {
            "resourceType": "Patient",
            "identifier": identifiers,
            "name": [{
                "family": family_name,
                "given": given_names
            }],
            "gender": gender,
            "birthDate": birth_date
        }

    def convert_problems(self, ccda_doc: str) -> list:
        """Extract Conditions from C-CDA Problem List"""
        root = etree.fromstring(ccda_doc.encode())

        # Find problem section
        problem_section = root.find(
            ".//cda:section[cda:templateId[@root='2.16.840.1.113883.10.20.22.2.5.1']]",
            self.NAMESPACES
        )

        conditions = []
        for entry in problem_section.findall('.//cda:entry', self.NAMESPACES):
            problem_act = entry.find('cda:act', self.NAMESPACES)
            observation = problem_act.find('.//cda:observation', self.NAMESPACES)

            # Get code
            code_elem = observation.find('cda:value', self.NAMESPACES)
            snomed_code = code_elem.get('code')
            display_name = code_elem.get('displayName')

            # Get dates
            effective_time = observation.find('cda:effectiveTime', self.NAMESPACES)
            onset_date = self._parse_ccda_date(
                effective_time.find('cda:low', self.NAMESPACES).get('value')
            )

            condition = {
                "resourceType": "Condition",
                "code": {
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": snomed_code,
                        "display": display_name
                    }]
                },
                "onsetDateTime": onset_date
            }
            conditions.append(condition)

        return conditions

    def _parse_ccda_date(self, ccda_date: str) -> str:
        """Parse C-CDA date format to FHIR"""
        if len(ccda_date) >= 8:
            return f"{ccda_date[:4]}-{ccda_date[4:6]}-{ccda_date[6:8]}"
        return ccda_date
            ''',
        }

    # =========================================================================
    # FHIR SECURITY
    # =========================================================================

    @staticmethod
    def fhir_security() -> Dict[str, Any]:
        """FHIR Security and consent patterns"""
        return {
            "consent_resource": '''
// FHIR Consent resource for data sharing
{
  "resourceType": "Consent",
  "status": "active",
  "scope": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/consentscope",
      "code": "patient-privacy"
    }]
  },
  "category": [{
    "coding": [{
      "system": "http://loinc.org",
      "code": "59284-0",
      "display": "Consent Document"
    }]
  }],
  "patient": {
    "reference": "Patient/12345"
  },
  "dateTime": "2024-01-15T10:00:00Z",
  "performer": [{
    "reference": "Patient/12345"
  }],
  "organization": [{
    "reference": "Organization/hospital-abc"
  }],
  "sourceAttachment": {
    "contentType": "application/pdf",
    "url": "https://forms.hospital.org/consent/12345.pdf"
  },
  "provision": {
    "type": "permit",
    "period": {
      "start": "2024-01-15",
      "end": "2025-01-15"
    },
    "actor": [{
      "role": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
          "code": "CST",
          "display": "custodian"
        }]
      },
      "reference": {
        "reference": "Organization/insurance-xyz"
      }
    }],
    "action": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/consentaction",
        "code": "access"
      }]
    }],
    "purpose": [{
      "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
      "code": "TREAT",
      "display": "Treatment"
    }]
  }
}
            ''',
            "security_labels": '''
# Security labels on resources
{
  "resourceType": "Observation",
  "meta": {
    "security": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
        "code": "R",
        "display": "Restricted"
      },
      {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "PSY",
        "display": "Psychiatry"
      }
    ]
  },
  // ... rest of observation
}

# Server-side consent enforcement
class ConsentEnforcedFHIRServer:
    def get_resource(self, resource_type: str, resource_id: str, user_context: dict) -> dict:
        """Get resource with consent enforcement"""
        resource = fhir_store.read(resource_type, resource_id)

        # Get patient's consents
        patient_ref = resource.get("subject", {}).get("reference")
        consents = fhir_store.search("Consent", {"patient": patient_ref, "status": "active"})

        # Check if access is permitted
        if not self._is_access_permitted(resource, consents, user_context):
            raise AccessDenied("Access denied by patient consent")

        # Apply data masking based on consent
        masked_resource = self._apply_consent_restrictions(resource, consents)

        return masked_resource

    def _is_access_permitted(self, resource: dict, consents: list, user_context: dict) -> bool:
        """Check consent provisions"""
        for consent in consents:
            provision = consent.get("provision", {})

            # Check actor (who's requesting)
            permitted_actors = [a["reference"]["reference"] for a in provision.get("actor", [])]
            if user_context["organization"] not in permitted_actors:
                continue

            # Check purpose
            permitted_purposes = [p["code"] for p in provision.get("purpose", [])]
            if user_context["purpose"] not in permitted_purposes:
                continue

            # Check security labels
            resource_labels = resource.get("meta", {}).get("security", [])
            excluded_categories = [c["coding"][0]["code"] for c in provision.get("securityLabel", [])]
            if any(label["code"] in excluded_categories for label in resource_labels):
                continue

            return provision.get("type") == "permit"

        return False  # No matching consent found
            ''',
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        fhir_resource: str,
        profile_violated: str,
        current_implementation: str,
        compliant_implementation: str,
    ) -> FHIRFinding:
        """Generate a structured finding"""
        return FHIRFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            fhir_resource=fhir_resource,
            profile_violated=profile_violated,
            current_implementation=current_implementation,
            compliant_implementation=compliant_implementation,
            tools=self.get_tool_recommendations(),
            remediation={
                "effort": "MEDIUM" if severity in ["LOW", "MEDIUM"] else "HIGH",
                "priority": severity
            }
        )

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended tools for FHIR compliance"""
        return [
            {
                "name": "HAPI FHIR Validator",
                "command": "java -jar validator_cli.jar resource.json -version 4.0",
                "description": "HL7 official FHIR resource validator"
            },
            {
                "name": "Inferno Framework",
                "command": "docker run infernoframework/inferno",
                "description": "ONC-certified testing for US Core and SMART"
            },
            {
                "name": "HAPI FHIR Server",
                "command": "docker run -p 8080:8080 hapiproject/hapi:latest",
                "description": "Reference FHIR server for testing"
            },
            {
                "name": "FHIR Shorthand (FSH)",
                "command": "sushi .",
                "description": "Author FHIR profiles using FSH language"
            },
            {
                "name": "fhir-validator",
                "command": "npm install -g fhir-validator && fhir-validator resource.json",
                "description": "Node.js FHIR validator"
            },
            {
                "name": "Synthea",
                "command": "java -jar synthea.jar -p 100",
                "description": "Generate synthetic FHIR patient data"
            },
        ]


def create_enhanced_fhir_assistant():
    """Factory function to create Enhanced FHIR Compliance Assistant"""
    return {
        "name": "Enhanced FHIR Compliance Reviewer",
        "version": "2.0.0",
        "system_prompt": """You are an expert FHIR healthcare interoperability specialist with comprehensive
knowledge of HL7 FHIR standards and healthcare data exchange. Your expertise covers:

FHIR STANDARDS:
- FHIR R4 and R5 resources, data types, and extensions
- Resource relationships and references
- RESTful API operations (CRUD, search, operations)
- Bundle types (transaction, batch, document, collection)
- CapabilityStatement and conformance

US CORE IMPLEMENTATION GUIDE:
- US Core profiles and required elements
- USCDI (US Core Data for Interoperability) data classes
- Extensions for race, ethnicity, birth sex
- Clinical data requirements for ONC certification

SMART ON FHIR:
- OAuth 2.0 authorization flows (EHR launch, standalone)
- SMART scopes and permissions
- Launch context (patient, encounter)
- Backend services authorization (client credentials)

CDS HOOKS:
- Hook definitions (patient-view, order-select, order-sign)
- Card responses and suggestions
- Prefetch templates
- Decision support integration

TERMINOLOGY SERVICES:
- ValueSet expansion and validation
- CodeSystem lookups
- ConceptMap translations
- SNOMED CT, LOINC, ICD-10, RxNorm

DATA EXCHANGE:
- Bulk Data Export ($export operation)
- Subscriptions (R4 webhooks, R5 topics)
- FHIR Documents (clinical documents)
- HL7 v2 to FHIR and C-CDA to FHIR mapping

Analyze FHIR implementations for compliance and interoperability issues.
Provide specific recommendations with profile references and code examples.

Format findings with affected profiles and severity levels.""",
        "assistant_class": EnhancedFHIRAssistant,
        "finding_model": FHIRFinding,
        "domain": "compliance",
        "subdomain": "fhir",
        "tags": ["fhir", "healthcare", "hl7", "interoperability", "smart", "us-core"],
        "tools": EnhancedFHIRAssistant.get_tool_recommendations(),
        "capabilities": [
            "profile_validation",
            "us_core_compliance",
            "smart_on_fhir_review",
            "cds_hooks_integration",
            "terminology_mapping",
            "bulk_data_export",
            "hl7v2_fhir_mapping"
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedFHIRAssistant()
    print(f"=== {assistant.name} v{assistant.version} ===\n")
    print(f"Standards: {', '.join(assistant.standards)}\n")

    # Demonstrate FHIR resources
    print("--- Core FHIR Resources ---")
    resources = assistant.fhir_resources()
    print("Patient: Demographics and identifiers")
    print("Observation: Clinical measurements and vital signs")

    # Demonstrate SMART on FHIR
    print("\n--- SMART on FHIR ---")
    smart = assistant.smart_on_fhir()
    print("Scopes: patient/*.read, user/*.*, launch/patient")
    print("Launch flow: EHR redirect -> Authorization -> Token exchange")

    # Demonstrate CDS Hooks
    print("\n--- CDS Hooks ---")
    cds = assistant.cds_hooks()
    print("Hook types: patient-view, order-select, order-sign")
    print("Response: Cards with suggestions and actions")

    # Show US Core profiles
    print("\n--- US Core Profiles ---")
    us_core = assistant.us_core_profiles()
    print("US Core defines minimum required data elements for US healthcare")
    for profile in us_core["overview"]["required_profiles"][:5]:
        print(f"  - {profile}")

    # Show FHIR search
    print("\n--- FHIR Search ---")
    search = assistant.fhir_search()
    print("Basic: /Patient?name=smith")
    print("Chained: /Observation?patient.name=smith")
    print("Include: /Patient?_include=Patient:organization")

    # Show FHIR operations
    print("\n--- FHIR Operations ---")
    operations = assistant.fhir_operations()
    print("$everything: Get all data for a patient")
    print("$validate: Validate against profiles")
    print("$match: Patient matching")

    # Show subscriptions
    print("\n--- FHIR Subscriptions ---")
    subs = assistant.fhir_subscriptions()
    print("R4: REST hooks with criteria")
    print("R5: Topic-based subscriptions")

    # Show bulk data
    print("\n--- Bulk Data Export ---")
    bulk = assistant.bulk_data()
    print("GET /Patient/$export -> async job -> NDJSON files")

    # Show mapping
    print("\n--- FHIR Mapping ---")
    mapping = assistant.fhir_mapping()
    print("HL7 v2 to FHIR: ADT^A01 -> Encounter")
    print("C-CDA to FHIR: Document sections -> Resources")

    # Show security
    print("\n--- FHIR Security ---")
    security = assistant.fhir_security()
    print("Consent resource for data sharing permissions")
    print("Security labels for access control")

    # Generate sample finding
    print("\n--- Sample Finding ---")
    finding = assistant.generate_finding(
        finding_id="FHIR-001",
        title="Missing Required US Core Patient Elements",
        severity="HIGH",
        category="Profile Compliance",
        fhir_resource="Patient",
        profile_violated="US Core Patient",
        current_implementation="Patient resource missing identifier and gender",
        compliant_implementation="Add identifier (MRN) and gender as required by US Core"
    )
    print(f"ID: {finding.finding_id}")
    print(f"Title: {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"Profile Violated: {finding.profile_violated}")
    print(f"Remediation: {finding.remediation}")

    # Show tool recommendations
    print("\n--- Tool Recommendations ---")
    tools = assistant.get_tool_recommendations()
    for tool in tools[:4]:
        print(f"\n{tool['name']}:")
        print(f"  Command: {tool['command']}")
        print(f"  Description: {tool['description']}")

    # Show factory function output
    print("\n--- Factory Function ---")
    config = create_enhanced_fhir_assistant()
    print(f"Name: {config['name']}")
    print(f"Version: {config['version']}")
    print(f"Domain: {config['domain']}")
    print(f"Tags: {', '.join(config['tags'])}")
    print(f"Capabilities: {', '.join(config['capabilities'][:3])}...")
