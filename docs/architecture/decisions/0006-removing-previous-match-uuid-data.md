# 6. Removing Previous Match UUID Data

Date: 2024-01-05

## Status

Proposed

Partially supercedes [4. REST API Endpoints](0004-rest-api-endpoints.md)

## Context

As we chose to [remove some redundant data relationship](0005-removing-redundant-data-relationship.md),
some endpoints schemas need to be updated. This is a document to provide the changes in the updated endpoints.

Another change related to naming conflict is that the `competitors` attribute to represent the number of competitors
registered in a tournament is replaced with `numberCompetitors`.

Besides the schema changes, there is a missing error condition that we also include in this document.

## Decision

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
- Target *Competitor* is already registered in target *Tournament* (status code: 409 Conflict)
- Target *Tournament* has already created its matches and does not allow new *Competitor*s registration (status code: 409 Conflict)


### POST `/tournament/<tournament_uuid>/start`
Start a *Tournament* by closing its *Competitor*s registration, calculating all *Match*es and
return the *Tournament*, the *Competitor*s, and all of its *Match*es data.

The entry *Match*es will be randomly generated but each of them will have at least one *Competitor*.

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
    "matchForTournamentListing": {
      "type": "object",
      "required": [
        "uuid",
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
        "round": {
          "type": "integer",
          "minimum": 0
        },
        "position": {
          "type": "integer",
          "minimum": 0
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
    "numberCompetitors": 4
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
      "round": 0,
      "position": 0,
      "competitorA": null,
      "competitorB": null,
      "winner": null,
      "loser": null
    },
    {
      "uuid": "a9367a16-3f64-408b-9596-4029f7f60e62",
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
    "matchForTournamentListing": {
      "type": "object",
      "required": [
        "uuid",
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
        "round": {
          "type": "integer",
          "minimum": 0
        },
        "position": {
          "type": "integer",
          "minimum": 0
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
    "numberCompetitors": 4
  },
  "past": [
    {
      "uuid": "1e172084-ec76-4f56-bd8e-7b3c170e1221",
      "round": 1,
      "position": 0,
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


## Consequences

With the changes in the schema, we make it more straightforward to serialize data from the database.
