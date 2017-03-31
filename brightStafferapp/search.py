from django.conf import settings
import requests
import os
from django.core.management import call_command

term = "search_term"
false = 'false'
INDEX_NAME = 'haystack'
BASE_URL = settings.HAYSTACK_CONNECTIONS['default']['URL']
DELETE_QUERY = 'DELETE haystack'
MAPPING_QUERY = {
   "settings": {
      "index": {
         "number_of_shards": 4,
         "number_of_replicas": 2
      },
      "analysis": {
         "analyzer": {
            "email_analyzer": {
               "tokenizer": "my_tokenizer"
            }
         },
         "tokenizer": {
            "my_tokenizer": {
               "type": "uax_url_email"
            }
         }
      }
   }
}
INDEX_MAPPING = {
   "properties": {
      "activation_date": {
         "type": "date",
         "format": "dd/mm/yyyy"
      },
      "create_date": {
         "type": "date",
         "format": "dd/mm/yyyy HH:mm:ss"
      },
      "current_location": {
         "type": "text"
      },
      "designation": {
         "type": "text"
      },
      "django_ct": {
         "type": "keyword",
         "include_in_all": false
      },
      "django_id": {
         "type": "keyword",
         "include_in_all": false
      },
      "id": {
         "type": "text"
      },
      "industry_focus": {
         "type": "text"
      },
      "industry_focus_percentage": {
         "type": "text"
      },
      "linkedin_url": {
         "type": "text"
      },
      "rating": {
         "type": "text"
      },
      "recruiter": {
          "type": "string",
          "analyzer": "email_analyzer"
        },
      "status": {
         "type": "text"
      },
      "talent_company": {
         "type": "nested",
         "properties": {
            "career_gap": {
               "type": "long"
            },
            "company": {
               "type": "text"
            },
            "designation": {
               "type": "text"
            },
            "end_date": {
               "type": "text"
            },
            "is_current": {
               "type": "boolean"
            },
            "start_date": {
               "type": "text"
            },
            "talent": {
               "type": "text"
            },
            "years_of_experience": {
               "type": "float"
            }
         }
      },
      "recruiter_active": {
            "type": "nested",
            "properties": {
               "recruiter": {
                  "type": "string",
                  "analyzer": "email_analyzer"
               },
               "is_active": {
                  "type": "boolean"
               }
            }
         },
      "talent_concepts": {
         "type": "nested",
         "properties": {
            "concept": {
               "type": "text"
            },
            "date_created": {
               "type": "text"
            },
            "match": {
               "type": "float"
            },
            "talent": {
               "type": "text"
            }
         }
      },
      "talent_contact": {
         "type": "nested",
         "properties": {
            "contact": {
               "type": "text"
            },
            "is_primary": {
               "type": "boolean"
            },
            "talent": {
               "type": "text"
            }
         }
      },
      "talent_education": {
         "type": "nested",
         "properties": {
            "course": {
               "type": "text"
            },
            "education": {
               "type": "text"
            },
            "end_date": {
               "type": "text"
            },
            "start_date": {
               "type": "text"
            },
            "talent": {
               "type": "text"
            }
         }
      },
      "talent_email": {
         "type": "nested",
         "properties": {
            "email": {
               "type": "text"
            },
            "is_primary": {
               "type": "boolean"
            },
            "talent": {
               "type": "text"
            }
         }
      },
      "talent_name": {
         "type": "text"
      },
      "talent_project": {
         "type": "nested",
         "properties": {
            "company_name": {
               "type": "text"
            },
            "date_added": {
               "type": "text"
            },
            "project": {
               "type": "text"
            },
            "project_match": {
               "type": "float"
            },
            "project_stage": {
               "type": "text"
            },
            "rank": {
               "type": "long"
            },
            "talent": {
               "type": "text"
            }
         }
      },
      "talent_stages": {
         "type": "nested",
         "properties": {
            "date_created": {
               "type": "date",
               "format": "dd/mm/yyyy"
            },
            "date_updated": {
               "type": "date",
               "format": "dd/mm/yyyy"
            },
            "details": {
               "type": "text"
            },
            "notes": {
               "type": "text"
            },
            "project": {
               "type": "text"
            },
            "stage": {
               "type": "text",
               "analyzer": "keyword"
            },
            "talent": {
               "type": "text"
            }
         }
      },
      "text": {
         "type": "text"
      }
   }
}


def delete_index():
    response = requests.delete(os.path.join(BASE_URL + INDEX_NAME))
    if response.status_code == 200:
        print("Index deleted with status code 200.")
    else:
        print("Error deleting index. Please check if index exists or not.")


def create_index():
    payload = MAPPING_QUERY
    response = requests.put(os.path.join(BASE_URL, INDEX_NAME), json=payload)
    if response.status_code == 200:
        print("Index created with status code 200.")
    else:
        print("Error creating index. Please check if index exists or not.")


def put_mapping():
    payload = INDEX_MAPPING
    response = requests.put(os.path.join(BASE_URL, INDEX_NAME, 'modelresult/_mapping'), json=payload)

    if response.status_code == 200:
        print("Index mapping updated with status code 200.")
    else:
        print("Error creating mapping. Please check if index exists or not.")


def rebuild_search():
    try:
        delete_index()
        create_index()
        put_mapping()
        call_command('update_index')
    except Exception as e:
        print("Process failed with following exception {}".format(e))

EMPTY_QUERY = {
            "hits": [],
            "max_score": "null",
            "total": 0
        }

BASE_QUERY = {
   "sort": [
      {
         "create_date": {
            "order": "desc"
         }
      }
   ],
   "from": 0,
   "size": 10,
   "query": {
        "bool": {
            "must": {
                "match_all": {}
            },
            "filter": {
                "bool": {
                    "should": [],
                    "must": [
                       {"match": {"recruiter": "recruiter_term"}},
                       {"terms": {"status": ["active", "new"]}},
                       {
                        "nested": {
                           "path": "recruiter_active",
                           "query": {
                              "bool": {
                                 "must": [
                                    {"match": {"recruiter_active.recruiter": "recruiter_term"}},
                                    {"match": {"recruiter_active.is_active":  "true"}}
                                 ]
                              }
                           }
                        }
                       },
                    ]
                }
            }
        }
    }
                }
TERM_QUERY = {
   "sort": [
         {
            "create_date": {
               "order": "desc"
            }
         }
      ],
   "from": 0,
   "size": 10,
   "query": {
      "bool": {
         "must": {
            "match_all": {}
         },
         "filter": {
            "bool": {
               "should": [
                  {
                     "nested": {
                        "path": "talent_company",
                        "query": {
                           "multi_match": {
                              "query": "search_term",
                              "fields": [
                                 "talent_company.company",
                                 "talent_company.talent",
                                 "talent_company.designation"
                              ]
                           }
                        }
                     }
                  },
                  {
                     "nested": {
                        "path": "talent_project",
                        "query": {
                           "multi_match": {
                              "query": "search_term",
                              "fields": [
                                 "talent_project.project",
                                 "talent_project.talent",
                                 "talent_project.project_stage"
                              ]
                           }
                        }
                     }
                  },
                  {
                     "nested": {
                        "path": "talent_concepts",
                        "query": {
                           "multi_match": {
                              "query": "search_term",
                              "fields": [
                                 "talent_concepts.concept",
                                 "talent_concepts.match"
                              ]
                           }
                        }
                     }
                  },
                  {
                     "nested": {
                        "path": "talent_education",
                        "query": {
                           "multi_match": {
                              "query": "search_term",
                              "fields": [
                                 "talent_education.education",
                                 "talent_education.course"
                              ]
                           }
                        }
                     }
                  },
                  {
                     "nested": {
                        "path": "talent_stages",
                        "query": {
                           "multi_match": {
                              "query": "search_term",
                              "fields": [
                                 "talent_stages.notes",
                                 "talent_stages.details",
                                 "talent_stages.project"
                              ]
                           }
                        }
                     }
                  },
                  {
                     "nested": {
                        "path": "talent_email",
                        "query": {
                           "match": {
                              "talent_email.email": "search_term"
                           }
                        }
                     }
                  },
                  {
                     "nested": {
                        "path": "talent_contact",
                        "query": {
                           "match": {
                              "talent_contact.contact": "search_term"
                           }
                        }
                     }
                  },
                  {
                     "multi_match": {
                        "query": "search_term",
                        "fields": [
                           "talent_name",
                           "designation",
                           "company",
                           "current_location",
                           "industry_focus"
                        ]
                     }
                  }
               ],
               "must": [
                  {"match": {"recruiter": "recruiter_term"}},
                  {"terms": {"status": ["active", "new"]}},
                  {
                        "nested": {
                           "path": "recruiter_active",
                           "query": {
                              "bool": {
                                 "must": [
                                    {"match": {"recruiter_active.recruiter": "recruiter_term"}},
                                    {"match": {"recruiter_active.is_active":  "true"}}
                                 ]
                              }
                           }
                        }
                  }
               ]
            }
         }
      }
   }
}
