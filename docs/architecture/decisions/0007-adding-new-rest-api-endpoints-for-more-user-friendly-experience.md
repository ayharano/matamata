# 7. Adding New REST API Endpoints for More User-Friendly Experience

Date: 2024-01-09

## Status

Proposed

Partially supercedes [4. REST API Endpoints](0004-rest-api-endpoints.md)

## Context

In the decision documents
[4. REST API Endpoints](0004-rest-api-endpoints.md)
and
[6. Removing Previous Match UUID Data](0006-removing-previous-match-uuid-data.md),
we provide several REST API endpoints that allow a tournament to be managed end to end.

However, after analyzing the flow of a
[single-elimination tournament](https://en.wikipedia.org/wiki/Single-elimination_tournament),
it can be seen that the current endpoints require a
[User](0002-defining-ubiquitous-language.md#user)
to keep track of resource UUIDs.

For example, if a
[Tournament](0002-defining-ubiquitous-language.md#tournament)
is created, the client needs to locally store the UUID of that resource to interact with it:
based on the current design, there is no endpoint that allows a User to retrieve the UUID of
the previously created tournament.

Another example is that two different clients cannot interact with the same Tournament unless
the UUID of the target Tournament is provided externally.

This document describes a new set of REST API endpoints to allow a User to interact with the system
beyond the minimum tournament management interactions.

## Decision

### GET `/competitor`
List all the registered *Competitor*s in the system.

#### Payload
Not Applicable

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responseGetCompetitor",
  "type": "object",
  "required": ["competitors"],
  "properties": {
    "competitors": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/competitor"
      }
    }
  },
  "$defs": {
    "competitor": {
      "type": "object",
      "required": ["uuid", "label"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Competitor identifier"
        },
        "label": {
          "type": "string",
          "description": "Competitor textual representation"
        }
      }
    }
  }
}
```

##### Example
JSON:
```json
{
  "competitors": [
    {
      "uuid": "de686e37-804b-4815-a507-d5879a240af6",
      "label": "Germany"
    },
    {
      "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
      "label": "South Korea"
    },
    {
      "uuid": "7f026276-0904-4a7b-ae14-8c66b95ffc9e",
      "label": "Brazil"
    },
    {
      "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
      "label": "Turkey"
    }
  ]
}
```


### GET `/competitor/<competitor_uuid>`
Get the data of a *Competitor*, including a list the registered tournaments split into past, ongoing, and upcoming.

#### Payload
Not Applicable

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responseGetCompetitorDetail",
  "type": "object",
  "required": ["competitor", "tournaments"],
  "properties": {
    "competitor": {
      "$ref": "#/$defs/competitor"
    },
    "tournaments": {
      "type": "object",
      "required": ["past", "ongoing", "upcoming"],
      "properties": {
        "past": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/tournament"
          }
        },
        "ongoing": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/tournament"
          }
        },
        "upcoming": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/tournament"
          }
        }
      }
    }
  },
  "$defs": {
    "competitor": {
      "type": "object",
      "required": ["uuid", "label"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Competitor identifier"
        },
        "label": {
          "type": "string",
          "description": "Competitor textual representation"
        }
      }
    },
    "tournament": {
      "type": "object",
      "required": ["uuid", "label"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Tournament identifier"
        },
        "label": {
          "type": "string",
          "description": "Tournament textual representation"
        }
      }
    }
  }
}
```

##### Example
```json
{
  "competitor": {
    "uuid": "de686e37-804b-4815-a507-d5879a240af6",
    "label": "Germany"
  },
  "tournaments": {
    "past": [
      {
        "uuid": "03c964f8-7f5c-4224-b848-1ab6c1413c7d",
        "label": "2002 FIFA World Cup"
      }
    ],
    "ongoing": [],
    "upcoming": []
  }
}
```

#### Error output
Status code: 4xx

JSON schema:
```json
{
  "title": "errorGetCompetitorDetail",
  "type": "object",
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error detail"
    }
  }
}
```

This endpoint might fail for one of the listed reasons:
- Target *Competitor* does not exist (status code: 404 Not Found)


### GET `/match/<match_uuid>`
Get the data of a *Match*.

#### Payload
Not Applicable

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responseGetMatchDetail",
  "type": "object",
  "required": [
    "uuid",
    "tournament",
    "round",
    "position",
    "competitorA",
    "competitorB",
    "winner",
    "loser"
  ],
  "properties": {
    "uuid": {
      "type": "string",
      "format": "uuid",
      "description": "Match identifier"
    },
    "tournament": {
      "$ref": "#/$defs/tournament"
    },
    "round": {
      "type": "integer",
      "minimum": 0
    },
    "position": {
      "type": "integer",
      "minimum": 0
    },
    "competitorA": {
      "$ref": "#/$defs/competitor"
    },
    "competitorB": {
      "$ref": "#/$defs/competitor"
    },
    "winner": {
      "$ref": "#/$defs/competitor"
    },
    "loser": {
      "$ref": "#/$defs/competitor"
    }
  },
  "$defs": {
    "tournament": {
      "type": "object",
      "required": ["uuid", "label", "startingRound", "numberCompetitors"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Tournament identifier"
        },
        "label": {
          "type": "string",
          "description": "Tournament textual representation"
        },
        "startingRound": {
          "type": "integer",
          "minimum": 0
        },
        "numberCompetitors": {
          "type": "integer",
          "minimum": 1
        }
      }
    },
    "competitor": {
      "type": "object",
      "required": [
        "uuid",
        "label"
      ],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Competitor identifier"
        },
        "label": {
          "type": "string",
          "description": "Competitor textual representation"
        }
      }
    }
  }
}
```

##### Example
```json
{
  "uuid": "a9367a16-3f64-408b-9596-4029f7f60e62",
  "tournament": {
    "uuid": "03c964f8-7f5c-4224-b848-1ab6c1413c7d",
    "label": "2002 FIFA World Cup",
    "startingRound": 1,
    "numberCompetitors": 4
  },
  "round": 0,
  "position": 0,
  "competitorA": {
    "uuid": "de686e37-804b-4815-a507-d5879a240af6",
    "label": "Germany"
  },
  "competitorB": {
    "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
    "label": "Brazil"
  },
  "winner": {
    "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
    "label": "Brazil"
  },
  "loser": {
    "uuid": "de686e37-804b-4815-a507-d5879a240af6",
    "label": "Germany"
  }
}
```

#### Error output
Status code: 4xx

JSON schema:
```json
{
  "title": "errorGetMatchDetail",
  "type": "object",
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error detail"
    }
  }
}
```

This endpoint might fail for one of the listed reasons:
- Target *Match* does not exist (status code: 404 Not Found)


### GET `/tournament`
List all the registered *Tournament*s in the system.

#### Payload
Not Applicable

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responseGetTournament",
  "type": "object",
  "required": ["tournaments"],
  "properties": {
    "tournaments": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/tournament"
      }
    }
  },
  "$defs": {
    "tournament": {
      "type": "object",
      "required": ["uuid", "label"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Tournament identifier"
        },
        "label": {
          "type": "string",
          "description": "Tournament textual representation"
        }
      }
    }
  }
}
```

##### Example
JSON:
```json
{
  "tournaments": [
    {
      "uuid": "03c964f8-7f5c-4224-b848-1ab6c1413c7d",
      "label": "2002 FIFA World Cup"
    }
  ]
}
```


### GET `/tournament/<tournament_uuid>/competitor`
List the registered competitors of the target tournament.

#### Payload
Not Applicable

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responseGetTournamentCompetitor",
  "type": "object",
  "required": ["tournament", "competitors"],
  "properties": {
    "tournament": {
      "$ref": "#/$defs/tournament"
    },
    "competitors": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/competitor"
      }
    }
  },
  "$defs": {
    "tournament": {
      "type": "object",
      "required": ["uuid", "label"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Tournament identifier"
        },
        "label": {
          "type": "string",
          "description": "Tournament textual representation"
        }
      }
    },
    "competitor": {
      "type": "object",
      "required": ["uuid", "label"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Competitor identifier"
        },
        "label": {
          "type": "string",
          "description": "Competitor textual representation"
        }
      }
    }
  }
}
```

##### Example
```json
{
  "tournament": {
    "uuid": "03c964f8-7f5c-4224-b848-1ab6c1413c7d",
    "label": "2002 FIFA World Cup"
  },
  "competitors": [
    {
      "uuid": "de686e37-804b-4815-a507-d5879a240af6",
      "label": "Germany"
    },
    {
      "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
      "label": "South Korea"
    },
    {
      "uuid": "7f026276-0904-4a7b-ae14-8c66b95ffc9e",
      "label": "Brazil"
    }
  ]
}
```

#### Error output
Status code: 4xx

JSON schema:
```json
{
  "title": "errorGetTournamentCompetitor",
  "type": "object",
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error detail"
    }
  }
}
```

This endpoint might fail for one of the listed reasons:
- Target *Tournament* does not exist (status code: 404 Not Found)


### GET `/tournament/<tournament_uuid>/competitor/<competitor_uuid>`
List the target competitor matches in the target tournament: the result is split into past matches and upcoming matches.

#### Payload
Not Applicable

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responseGetTournamentCompetitorMatches",
  "type": "object",
  "required": ["tournament", "competitor", "matches"],
  "properties": {
    "tournament": {
      "$ref": "#/$defs/tournament"
    },
    "competitor": {
      "$ref": "#/$defs/competitor"
    },
    "matches": {
      "type": "object",
      "required": ["past", "upcoming"],
      "properties": {
        "past": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/matchForTournamentListingWithOtherCompetitor"
          }
        },
        "upcoming": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/matchForTournamentListingWithOtherCompetitor"
          }
        }
      }
    }
  },
  "$defs": {
    "tournament": {
      "type": "object",
      "required": ["uuid", "label", "startingRound", "numberCompetitors"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Tournament identifier"
        },
        "label": {
          "type": "string",
          "description": "Tournament textual representation"
        },
        "startingRound": {
          "type": "integer",
          "minimum": 0
        },
        "numberCompetitors": {
          "type": "integer",
          "minimum": 1
        }
      }
    },
    "competitor": {
      "type": "object",
      "required": ["uuid", "label"],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Competitor identifier"
        },
        "label": {
          "type": "string",
          "description": "Competitor textual representation"
        }
      }
    },
    "matchForTournamentListingWithOtherCompetitor": {
      "type": "object",
      "required": [
        "uuid",
        "round",
        "position",
        "otherCompetitor"
      ],
      "properties": {
        "uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Match identifier"
        },
        "round": {
          "type": "integer",
          "minimum": 0
        },
        "position": {
          "type": "integer",
          "minimum": 0
        },
        "otherCompetitor": {
          "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/competitor"}
          ]
        }
      }
    }
  }
}
```

##### Example
```json
{
  "tournament": {
    "uuid": "03c964f8-7f5c-4224-b848-1ab6c1413c7d",
    "label": "2002 FIFA World Cup",
    "startingRound": 1,
    "numberCompetitors": 4
  },
  "competitor": {
    "uuid": "7f026276-0904-4a7b-ae14-8c66b95ffc9e",
    "label": "Brazil"
  },
  "matches": {
    "past": [
      {
        "uuid": "3866cad6-ba40-44fb-96c6-09f1131c5649",
        "round": 1,
        "position": 1,
        "otherCompetitor": {
          "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
          "label": "Turkey"
        }
      }
    ],
    "upcoming": [
      {
        "uuid": "1f1fc156-4382-427c-aefb-5ae10009b7ce",
        "round": 0,
        "position": 0,
        "otherCompetitor": {
          "uuid": "de686e37-804b-4815-a507-d5879a240af6",
          "label": "Germany"
        }
      }
    ]
  }
}
```

#### Error output
Status code: 4xx

JSON schema:
```json
{
  "title": "errorGetTournamentCompetitorMatches",
  "type": "object",
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error detail"
    }
  }
}
```

This endpoint might fail for one of the listed reasons:
- Target *Competitor* does not exist (status code: 404 Not Found)
- Target *Tournament* does not exist (status code: 404 Not Found)
- Target *Competitor* is not registered for started target *Tournament* (status code: 409 Conflict)
- Target *Competitor* is not registered for unstarted target *Tournament* (status code: 422 Unprocessable Content)
- Target *Tournament* has not created its matches yet (status code: 422 Unprocessable Content)


## Consequences

The introduction of the new endpoints described in this document will directly improve the usability of the system.
This is achieved by expanding the REST API endpoints, offering a more flexible and easy-to-use experience.
