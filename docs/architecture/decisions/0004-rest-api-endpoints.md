# 4. REST API Endpoints

Date: 2024-01-02

## Status

Proposed

## Context

We defined [the ubiquitous language and the rules that the system will obey](0002-defining-ubiquitous-language.md)
and most of [the system data modeling](0003-data-modeling.md).

We need to define the interface that the system will make available for the
[User](0002-defining-ubiquitous-language.md#user)
interaction.

This document contains a non-exhaustive list of methods and endpoints that will be available for
a user to interact with the [single-elimination tournament](https://en.wikipedia.org/wiki/Single-elimination_tournament) management system.

## Decision

While we defined several fields for database tables in [the system data modeling](0003-data-modeling.md),
for the external input and output schemas some fields may be calculated or omitted during the user interaction.

For this document, we are using [JSON schema](https://json-schema.org/) with examples to display
the expected payload and results. The tournament used as an example is
[the 2002 FIFA World Cup](https://en.wikipedia.org/wiki/2002_FIFA_World_Cup),
starting from the semi-finals, to keep the examples short.

### POST `/competitor`
Create a *Competitor* without any *Tournament* registration and return the *Competitor* data.

#### Payload
JSON schema:
```json
{
  "title": "payloadPostCompetitor",
  "type": "object",
  "required": ["label"],
  "properties": {
    "label": {
      "type": "string",
      "description": "Competitor textual representation"
    }
  }
}
```

`label` is a textual data to represent a competitor. Its uniqueness isn't enforced by the system.

##### Example
JSON:
```json
{
  "label": "South Korea"
}
```

#### Successful output
Status code: 201 Created

JSON schema:
```json
{
  "title": "responsePostCompetitor",
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
```

##### Example
JSON:
```json
{
  "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
  "label": "South Korea"
}
```


### POST `/tournament`
Create a *Tournament* without any *Competitor* registration and return the *Tournament* data.

#### Payload
JSON schema:
```json
{
  "title": "payloadPostTournament",
  "type": "object",
  "required": ["label"],
  "properties": {
    "label": {
      "type": "string",
      "description": "Tournament textual representation"
    }
  }
}
```

`label` is a textual data to represent a tournament. Its uniqueness isn't enforced by the system.

##### Example
```json
{
  "label": "2002 FIFA World Cup"
}
```

#### Successful output
Status code: 201 Created

JSON schema:
```json
{
  "title": "responsePostTournament",
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
```

##### Example
```json
{
  "uuid": "03c964f8-7f5c-4224-b848-1ab6c1413c7d",
  "label": "2002 FIFA World Cup"
}
```


### POST `/tournament/<tournament_uuid>/competitor`
Register a *Competitor* into a *Tournament* and return the *Tournament*-*Competitor* association data.

#### Payload
JSON schema:
```json
{
  "title": "payloadPostTournamentCompetitor",
  "type": "object",
  "required": ["competitor_uuid"],
  "properties": {
    "competitor_uuid": {
      "type": "string",
      "format": "uuid",
      "description": "Competitor identifier"
    }
  }
}
```

`competitor_uuid` is the UUID of a previously created competitor to be registered into the target tournament.

##### Example
```json
{
  "competitor_uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9"
}
```

#### Successful output
Status code: 201 Created

JSON schema:
```json
{
  "title": "responsePostTournamentCompetitor",
  "type": "object",
  "required": ["tournament", "competitor"],
  "properties": {
    "tournament": {
      "$ref": "#/$defs/tournament"
    },
    "competitor": {
      "$ref": "#/$defs/competitor"
    }
  },
  "$defs": {
    "tournament": {
      "type": "object",
      "required": [
        "uuid",
        "label"
      ],
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
  "tournament": {
    "uuid": "03c964f8-7f5c-4224-b848-1ab6c1413c7d",
    "label": "2002 FIFA World Cup"
  },
  "competitor": {
    "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
    "label": "South Korea"
  }
}
```

#### Error output
Status code: 4xx

JSON schema:
```json
{
  "title": "errorPostTournamentCompetitor",
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
- Target *Tournament* has already created its matches and does not allow new *Competitor*s registration (status code: 409 Conflict)


### POST `/tournament/<tournament_uuid>/start`
Start a *Tournament* by closing its *Competitor*s registration, calculating all *Match*es and
return the *Tournament*, the *Competitor*s, and all of its *Match*es data.

The entry *Match*es will be randomly generated but each of them will have at least one *Competitor*,
while all the intermediate *Match*es will have their `previousMatchX_uuid` and `previousMatchY_uuid`
properly populated with non-`null` values.

If there are entry *Match*es with only one *Competitor*, the next round's match will be filled with
the same *Competitor* reference, being the same as an automatic winning.

#### Payload
Not Applicable

#### Successful output
Status code: 201 Created

JSON schema:
```json
{
  "title": "responsePostTournamentStart",
  "type": "object",
  "required": ["tournament", "competitors", "matches"],
  "properties": {
    "tournament": {
      "$ref": "#/$defs/tournament"
    },
    "competitors": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/competitor"
      }
    },
    "matches": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/matchForTournamentListing"
      }
    }
  },
  "$defs": {
    "tournament": {
      "type": "object",
      "required": ["uuid", "label", "startingRound", "competitors"],
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
        "competitors": {
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
    "matchForTournamentListing": {
      "type": "object",
      "required": [
        "uuid",
        "round",
        "position",
        "previousMatchX_uuid",
        "previousMatchY_uuid",
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
        "round": {
          "type": "integer",
          "minimum": 0
        },
        "position": {
          "type": "integer",
          "minimum": 0
        },
        "previousMatchX_uuid": {
          "type": ["string", "null"],
          "format": "uuid",
          "description": "Previous Match X identifier"
        },
        "previousMatchY_uuid": {
          "type": ["string", "null"],
          "format": "uuid",
          "description": "Previous Match Y identifier"
        },
        "competitorA": {
          "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/competitor"}
          ]
        },
        "competitorB": {
          "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/competitor"}
          ]
        },
        "winner": {
          "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/competitor"}
          ]
        },
        "loser": {
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
    "competitors": 4
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
    },
    {
      "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
      "label": "Turkey"
    }
  ],
  "matches": [
    {
      "uuid": "1e172084-ec76-4f56-bd8e-7b3c170e1221",
      "round": 1,
      "position": 0,
      "previousMatchX_uuid": null,
      "previousMatchY_uuid": null,
      "competitorA": {
        "uuid": "de686e37-804b-4815-a507-d5879a240af6",
        "label": "Germany"
      },
      "competitorB": {
        "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
        "label": "South Korea"
      },
      "winner": null,
      "loser": null
    },
    {
      "uuid": "3866cad6-ba40-44fb-96c6-09f1131c5649",
      "round": 1,
      "position": 1,
      "previousMatchX_uuid": null,
      "previousMatchY_uuid": null,
      "competitorA": {
        "uuid": "7f026276-0904-4a7b-ae14-8c66b95ffc9e",
        "label": "Brazil"
      },
      "competitorB": {
        "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
        "label": "Turkey"
      },
      "winner": null,
      "loser": null
    },
    {
      "uuid": "1f1fc156-4382-427c-aefb-5ae10009b7ce",
      "previousMatchX_uuid": "1e172084-ec76-4f56-bd8e-7b3c170e1221",
      "previousMatchY_uuid": "3866cad6-ba40-44fb-96c6-09f1131c5649",
      "round": 0,
      "position": 0,
      "competitorA": null,
      "competitorB": null,
      "winner": null,
      "loser": null
    },
    {
      "uuid": "a9367a16-3f64-408b-9596-4029f7f60e62",
      "previousMatchX_uuid": "1e172084-ec76-4f56-bd8e-7b3c170e1221",
      "previousMatchY_uuid": "3866cad6-ba40-44fb-96c6-09f1131c5649",
      "round": 0,
      "position": 1,
      "competitorA": null,
      "competitorB": null,
      "winner": null,
      "loser": null
    }
  ]
}
```

#### Error output
Status code: 4xx

JSON schema:
```json
{
  "title": "errorPostTournamentStart",
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
- Target *Tournament* does not have one *Competitor* registered yet (status code: 422 Unprocessable Content)
- Target *Tournament* has already created its matches (status code: 409 Conflict)


### GET `/tournament/<tournament_uuid>/match`
List the matches of the target tournament: the result is split into past matches and upcoming matches.

#### Payload
Not Applicable

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responseGetTournamentMatch",
  "type": "object",
  "required": ["tournament", "past", "upcoming"],
  "properties": {
    "tournament": {
      "$ref": "#/$defs/tournament"
    },
    "past": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/matchForTournamentListing"
      }
    },
    "upcoming": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/matchForTournamentListing"
      }
    }
  },
  "$defs": {
    "tournament": {
      "type": "object",
      "required": ["uuid", "label", "startingRound", "competitors"],
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
        "competitors": {
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
    "matchForTournamentListing": {
      "type": "object",
      "required": [
        "uuid",
        "round",
        "position",
        "previousMatchX_uuid",
        "previousMatchY_uuid",
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
        "round": {
          "type": "integer",
          "minimum": 0
        },
        "position": {
          "type": "integer",
          "minimum": 0
        },
        "previousMatchX_uuid": {
          "type": ["string", "null"],
          "format": "uuid",
          "description": "Previous Match X identifier"
        },
        "previousMatchY_uuid": {
          "type": ["string", "null"],
          "format": "uuid",
          "description": "Previous Match Y identifier"
        },
        "competitorA": {
          "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/competitor"}
          ]
        },
        "competitorB": {
          "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/competitor"}
          ]
        },
        "winner": {
          "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/competitor"}
          ]
        },
        "loser": {
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
    "competitors": 4
  },
  "past": [
    {
      "uuid": "1e172084-ec76-4f56-bd8e-7b3c170e1221",
      "round": 1,
      "position": 0,
      "previousMatchX_uuid": null,
      "previousMatchY_uuid": null,
      "competitorA": {
        "uuid": "de686e37-804b-4815-a507-d5879a240af6",
        "label": "Germany"
      },
      "competitorB": {
        "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
        "label": "South Korea"
      },
      "winner": {
        "uuid": "de686e37-804b-4815-a507-d5879a240af6",
        "label": "Germany"
      },
      "loser": {
        "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
        "label": "South Korea"
      }
    },
    {
      "uuid": "3866cad6-ba40-44fb-96c6-09f1131c5649",
      "round": 1,
      "position": 1,
      "previousMatchX_uuid": null,
      "previousMatchY_uuid": null,
      "competitorA": {
        "uuid": "7f026276-0904-4a7b-ae14-8c66b95ffc9e",
        "label": "Brazil"
      },
      "competitorB": {
        "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
        "label": "Turkey"
      },
      "winner": {
        "uuid": "7f026276-0904-4a7b-ae14-8c66b95ffc9e",
        "label": "Brazil"
      },
      "loser": {
        "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
        "label": "Turkey"
      }
    },
    {
      "uuid": "a9367a16-3f64-408b-9596-4029f7f60e62",
      "round": 0,
      "position": 1,
      "previousMatchX_uuid": "1e172084-ec76-4f56-bd8e-7b3c170e1221",
      "previousMatchY_uuid": "3866cad6-ba40-44fb-96c6-09f1131c5649",
      "competitorA": {
        "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
        "label": "South Korea"
      },
      "competitorB": {
        "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
        "label": "Turkey"
      },
      "winner": {
        "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
        "label": "Turkey"
      },
      "loser": {
        "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
        "label": "South Korea"
      }
    }
  ],
  "upcoming": [
    {
      "uuid": "1f1fc156-4382-427c-aefb-5ae10009b7ce",
      "round": 0,
      "position": 0,
      "previousMatchX_uuid": "1e172084-ec76-4f56-bd8e-7b3c170e1221",
      "previousMatchY_uuid": "3866cad6-ba40-44fb-96c6-09f1131c5649",
      "competitorA": {
        "uuid": "de686e37-804b-4815-a507-d5879a240af6",
        "label": "Germany"
      },
      "competitorB": {
        "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
        "label": "Brazil"
      },
      "winner": null,
      "loser": null
    }
  ]
}
```

#### Error output
Status code: 4xx

JSON schema:
```json
{
  "title": "errorGetTournamentMatch",
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
- Target *Tournament* has not created its matches yet (status code: 422 Unprocessable Content)


### POST `/match/<match_uuid>`
Register a *Match* result and return the updated *Match* data.

#### Payload
JSON schema:
```json
{
  "title": "payloadPostMatchResult",
  "type": "object",
  "required": ["winner_uuid"],
  "properties": {
    "winner_uuid": {
      "type": "string",
      "format": "uuid",
      "description": "Winner competitor identifier"
    }
  }
}
```

`winner_uuid` is the UUID of a match competitor to be registered as the match winner.

##### Example
```json
{
  "winner_uuid": "7f026276-0904-4a7b-ae14-8c66b95ffc9e"
}
```

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responsePostMatchResult",
  "type": "object",
  "required": [
    "uuid",
    "tournament",
    "round",
    "position",
    "previousMatchX_uuid",
    "previousMatchY_uuid",
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
    "previousMatchX_uuid": {
      "type": "string",
      "format": "uuid",
      "description": "Previous Match X identifier"
    },
    "previousMatchY_uuid": {
      "type": "string",
      "format": "uuid",
      "description": "Previous Match Y identifier"
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
      "required": ["uuid", "label", "startingRound", "competitors"],
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
        "competitors": {
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
    "competitors": 4
  },
  "round": 0,
  "position": 0,
  "previousMatchX_uuid": "1e172084-ec76-4f56-bd8e-7b3c170e1221",
  "previousMatchY_uuid": "3866cad6-ba40-44fb-96c6-09f1131c5649",
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
  "title": "errorPostMatchResult",
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
- Target *Match* has already registered its result (status code: 409 Conflict)
- Target *Match* is not ready to register a result due to registered previous *Match*es but missing *Competitor* (status code: 422 Unprocessable Content)


### GET `/tournament/<tournament_uuid>/result`
List the top 4 competitors of the target tournament if possible.
The competitors are listed as [final winner, final loser, third place winner, third place loser].
If there are less than 4 competitors, the missing values are replaced with `null`.

#### Payload
Not Applicable

#### Successful output
Status code: 200 OK

JSON schema:
```json
{
  "title": "responseGetTournamentResult",
  "type": "object",
  "required": ["tournament", "top4"],
  "properties": {
    "tournament": {
      "$ref": "#/$defs/tournament"
    },
    "top4": {
      "type": "array",
      "minItems": 4,
      "maxItems": 4,
      "items": {
        "oneOf": [
          {"type": "null"},
          {"$ref": "#/$defs/competitor"}
        ]
      }
    }
  },
  "$defs": {
    "tournament": {
      "type": "object",
      "required": ["uuid", "label", "startingRound", "competitors"],
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
        "competitors": {
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
    "competitors": 4
  },
  "top4": [
    {
      "uuid": "7f026276-0904-4a7b-ae14-8c66b95ffc9e",
      "label": "Brazil"
    },
    {
      "uuid": "de686e37-804b-4815-a507-d5879a240af6",
      "label": "Germany"
    },
    {
      "uuid": "15f4fe33-f317-4c4a-96e0-3b815dc481c6",
      "label": "Turkey"
    },
    {
      "uuid": "5d1bd1d1-2679-432a-ac11-ebfebfa1bce9",
      "label": "South Korea"
    }
  ]
}
```

#### Error output
Status code: 4xx

JSON schema:
```json
{
  "title": "errorGetTournamentResult",
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
- Target *Tournament* has not created its matches yet (status code: 422 Unprocessable Content)
- Target *Tournament* is not ready to display the top 4 competitors (status code: 422 Unprocessable Content)


### To be defined later

The proposed endpoints do not handle some common REST API structures,
such as pagination or the DELETE method.
If these or other modifications are necessary, they should be discussed in a future ADR.

## Consequences

Defining all the minimum required methods and endpoints allow us to
see whether we could potentially miss needed mechanisms for
a fully operational management system.
