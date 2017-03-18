term = "search_term"
TERM_QUERY = {"query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "talent_company",
                            "query": {
                                "multi_match": {
                                    "query": term,
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
                                    "query": term,
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
                                    "query": term,
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
                                    "query": term,
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
                                    "query": term,
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
                                    "talent_email.email": term
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "talent_contact",
                            "query": {
                                "match": {
                                    "talent_contact.contact": term
                                }
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": term,
                            "fields": [
                                "talent_name",
                                "designation",
                                "company",
                                "current_location",
                                "industry_focus"
                            ]
                        }
                    }
                ]
            }
        }
        }