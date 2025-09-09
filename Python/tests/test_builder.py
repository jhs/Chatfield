"""Unit tests for Chatfield builder pattern."""

from chatfield import chatfield


def describe_builder():
    """Tests for the builder API."""
    
    def describe_basic_usage():
        """Tests for basic builder functionality."""
        
        def it_creates_simple_interview():
            """Creates a simple interview with basic fields."""
            instance = (chatfield()
                .type("SimpleInterview")
                .desc("A simple interview")
                .field("name").desc("Your name")
                .field("email").desc("Your email")
                .build())
            
            meta = instance._chatfield
            assert meta['type'] == "SimpleInterview"
            assert meta['desc'] == "A simple interview"
            assert len(meta['fields']) == 2
            assert "name" in meta['fields']
            assert "email" in meta['fields']
            assert meta['fields']["name"]['desc'] == "Your name"
            assert meta['fields']["email"]['desc'] == "Your email"
        
        def it_adds_field_validation_rules():
            """Adds validation rules to fields."""
            instance = (chatfield()
                .type("ValidatedInterview")
                .field("field")
                    .desc("Test field")
                    .must("specific requirement")
                    .reject("avoid this")
                    .hint("Helpful tip")
                .build())
            
            field_meta = instance._chatfield['fields']["field"]
            assert "specific requirement" in field_meta['specs']['must']
            assert "avoid this" in field_meta['specs']['reject']
            assert "Helpful tip" in field_meta['specs']['hint']
        
        def it_supports_multiple_validation_rules():
            """Supports multiple validation rules on same field."""
            instance = (chatfield()
                .type("MultiRuleInterview")
                .field("field")
                    .desc("Test field")
                    .must("rule 1")
                    .must("rule 2")
                    .must("rule 3")
                .build())
            
            field_meta = instance._chatfield['fields']["field"]
            # Builder should maintain order
            assert field_meta['specs']['must'] == ["rule 1", "rule 2", "rule 3"]
        
        def it_supports_multiple_hints():
            """Supports multiple hints on same field."""
            instance = (chatfield()
                .type("MultiHintInterview")
                .field("field")
                    .desc("Test field with multiple hints")
                    .hint('First hint')
                    .hint('Second hint')
                    .hint('Third hint')
                .build())
            
            field_meta = instance._chatfield['fields']['field']
            assert field_meta['specs']['hint'] == ['First hint', 'Second hint', 'Third hint']
            assert len(field_meta['specs']['hint']) == 3
        
        def it_combines_all_field_features():
            """Combines all field feature types."""
            instance = (chatfield()
                .type("CombinedInterview")
                .field("complex_field")
                    .desc("Complex field")
                    .must("required info")
                    .reject("forbidden content")
                    .hint("Helpful guidance")
                .build())
            
            field_meta = instance._chatfield['fields']["complex_field"]
            
            assert field_meta['desc'] == "Complex field"
            assert "required info" in field_meta['specs']['must']
            assert "forbidden content" in field_meta['specs']['reject']
            assert "Helpful guidance" in field_meta['specs']['hint']

    def describe_role_configuration():
        """Tests for alice and bob role configuration."""
        
        def it_configures_alice_role():
            """Configures alice role type."""
            instance = (chatfield()
                .type("WithAlice")
                .alice().type("Senior Developer")
                .field("field").desc("Test field")
                .build())
            
            meta = instance._chatfield
            assert meta['roles']['alice']['type'] == "Senior Developer"
        
        def it_adds_alice_traits():
            """Adds traits to alice role."""
            instance = (chatfield()
                .type("WithAliceTraits")
                .alice()
                    .type("Interviewer")
                    .trait("patient")
                    .trait("thorough")
                .field("field").desc("Test field")
                .build())
            
            meta = instance._chatfield
            assert meta['roles']['alice']['type'] == "Interviewer"
            assert "patient" in meta['roles']['alice']['traits']
            assert "thorough" in meta['roles']['alice']['traits']
        
        def it_configures_bob_role():
            """Configures bob role type."""
            instance = (chatfield()
                .type("WithBob")
                .bob().type("Job Candidate")
                .field("field").desc("Test field")
                .build())
            
            meta = instance._chatfield
            assert meta['roles']['bob']['type'] == "Job Candidate"
        
        def it_adds_bob_traits():
            """Adds traits to bob role."""
            instance = (chatfield()
                .type("WithBobTraits")
                .bob()
                    .type("User")
                    .trait("technical")
                    .trait("curious")
                .field("field").desc("Test field")
                .build())
            
            meta = instance._chatfield
            assert meta['roles']['bob']['type'] == "User"
            assert "technical" in meta['roles']['bob']['traits']
            assert "curious" in meta['roles']['bob']['traits']
        
        def it_configures_both_roles():
            """Configures both alice and bob roles."""
            instance = (chatfield()
                .type("FullRoles")
                .desc("Test interview process")
                .alice()
                    .type("Interviewer")
                    .trait("professional")
                .bob()
                    .type("Candidate")
                    .trait("experienced")
                .field("field1").desc("First field")
                .field("field2").desc("Second field")
                .build())
            
            meta = instance._chatfield
            
            # Check description
            assert meta['desc'] == "Test interview process"
            
            # Check alice role
            assert meta['roles']['alice']['type'] == "Interviewer"
            assert "professional" in meta['roles']['alice']['traits']
            
            # Check bob role
            assert meta['roles']['bob']['type'] == "Candidate"
            assert "experienced" in meta['roles']['bob']['traits']
            
            # Check fields
            assert "field1" in meta['fields']
            assert "field2" in meta['fields']
            assert meta['fields']["field1"]['desc'] == "First field"
            assert meta['fields']["field2"]['desc'] == "Second field"

    def describe_transformations():
        """Tests for field transformation features."""
        
        def it_applies_type_transformations():
            """Applies basic type transformations."""
            instance = (chatfield()
                .type("TypedInterview")
                .field("age")
                    .desc("Your age")
                    .as_int()
                .field("salary")
                    .desc("Expected salary")
                    .as_float()
                .field("active")
                    .desc("Are you active?")
                    .as_bool()
                .field("confidence")
                    .desc("Confidence level")
                    .as_percent()
                .build())
            
            assert 'as_int' in instance._chatfield['fields']['age']['casts']
            assert 'as_float' in instance._chatfield['fields']['salary']['casts']
            assert 'as_bool' in instance._chatfield['fields']['active']['casts']
            assert 'as_percent' in instance._chatfield['fields']['confidence']['casts']
        
        def it_applies_language_transformations():
            """Applies language transformations."""
            instance = (chatfield()
                .type("MultiLangInterview")
                .field("greeting")
                    .desc("Say hello")
                    .as_lang('fr')
                    .as_lang('es')
                .build())
            
            field_casts = instance._chatfield['fields']['greeting']['casts']
            assert 'as_lang_fr' in field_casts
            assert 'as_lang_es' in field_casts
        
        def it_applies_custom_transformations():
            """Applies custom sub-attribute transformations."""
            instance = (chatfield()
                .type("CustomTransform")
                .field("number")
                    .desc("A number")
                    .as_bool('even', "True if even")
                    .as_str('uppercase', "In uppercase")
                .build())
            
            field_casts = instance._chatfield['fields']['number']['casts']
            assert 'as_bool_even' in field_casts
            assert 'as_str_uppercase' in field_casts
        
        def it_handles_choice_cardinality():
            """Handles choice cardinality options."""
            instance = (chatfield()
                .type("ChoiceInterview")
                .field("color")
                    .desc("Favorite color")
                    .as_one('selection', "red", "green", "blue")
                .field("priority")
                    .desc("Priority level")
                    .as_maybe('selection', "low", "medium", "high")
                .field("languages")
                    .desc("Programming languages")
                    .as_multi('selection', "python", "javascript", "rust")
                .field("reviewers")
                    .desc("Code reviewers")
                    .as_any('selection', "alice", "bob", "charlie")
                .build())
            
            # Verify choice casts were created correctly
            color_cast = instance._chatfield['fields']['color']['casts'].get('as_one_selection')
            assert color_cast is not None
            assert color_cast['type'] == 'choice'
            assert color_cast['choices'] == ['red', 'green', 'blue']
            assert color_cast['null'] is False
            assert color_cast['multi'] is False
            
            priority_cast = instance._chatfield['fields']['priority']['casts'].get('as_maybe_selection')
            assert priority_cast is not None
            assert priority_cast['type'] == 'choice'
            assert priority_cast['choices'] == ['low', 'medium', 'high']
            assert priority_cast['null'] is True
            assert priority_cast['multi'] is False
            
            lang_cast = instance._chatfield['fields']['languages']['casts'].get('as_multi_selection')
            assert lang_cast is not None
            assert lang_cast['type'] == 'choice'
            assert lang_cast['choices'] == ['python', 'javascript', 'rust']
            assert lang_cast['null'] is False
            assert lang_cast['multi'] is True
            
            reviewer_cast = instance._chatfield['fields']['reviewers']['casts'].get('as_any_selection')
            assert reviewer_cast is not None
            assert reviewer_cast['type'] == 'choice'
            assert reviewer_cast['choices'] == ['alice', 'bob', 'charlie']
            assert reviewer_cast['null'] is True
            assert reviewer_cast['multi'] is True

    def describe_special_fields():
        """Tests for special field features."""
        
        def it_marks_field_as_confidential():
            """Marks field as confidential."""
            instance = (chatfield()
                .type("ConfidentialInterview")
                .field("secret")
                    .desc("Secret information")
                    .confidential()
                .build())
            
            field = instance._chatfield['fields']['secret']
            assert field['specs']['confidential'] is True
        
        def it_marks_field_as_conclude():
            """Marks field as conclude (implies confidential)."""
            instance = (chatfield()
                .type("ConcludeInterview")
                .field("rating")
                    .desc("Final rating")
                    .conclude()
                .build())
            
            field = instance._chatfield['fields']['rating']
            assert field['specs']['conclude'] is True
            assert field['specs']['confidential'] is True  # Conclude implies confidential

    def describe_edge_cases():
        """Tests for edge cases and error conditions."""
        
        def it_creates_empty_interview():
            """Creates interview with no fields."""
            instance = (chatfield()
                .type("Empty")
                .desc("Empty interview")
                .build())
            
            meta = instance._chatfield
            assert meta['type'] == "Empty"
            assert meta['desc'] == "Empty interview"
            assert len(meta['fields']) == 0
        
        def it_creates_minimal_interview():
            """Creates interview with minimal configuration."""
            instance = chatfield().build()
            
            meta = instance._chatfield
            assert meta['type'] == ""
            assert meta['desc'] == ""
            assert len(meta['fields']) == 0
        
        def it_preserves_field_order():
            """Preserves field order during creation."""
            instance = (chatfield()
                .type("OrderedInterview")
                .field("first").desc("First")
                .field("second").desc("Second")
                .field("third").desc("Third")
                .field("fourth").desc("Fourth")
                .build())
            
            field_names = list(instance._chatfield['fields'].keys())
            assert field_names == ['first', 'second', 'third', 'fourth']