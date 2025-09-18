"""Custom DeepEval metrics for Chatfield evaluation."""

from .extraction_accuracy import FieldExtractionAccuracy, ExtractionCompletenessMetric
from .validation_compliance import MustRuleComplianceMetric, RejectPatternAvoidanceMetric, HintGuidanceMetric
from .vegan_compliance import VeganComplianceMetric, AnimalProductDetector, NaturalAcknowledgmentMetric
from .information_security import CastVisibilityMetric, AdversarialLeakageDetector, NaturalConversationMetric
from .exam_security import ExamAnswerProtectionMetric, SuspiciousBehaviorDetectionMetric, NeutralResponseMetric, HintPreventionMetric
from .tool_schema_security import (
    ToolSchemaProtectionMetric,
    FunctionEnumerationPreventionMetric,
    SchemaFormatLeakageMetric,
    ToolProbeDetectionMetric,
    ImplementationDetailsConcealmentMetric
)

__all__ = [
    # Extraction metrics
    'FieldExtractionAccuracy',
    'ExtractionCompletenessMetric',

    # Validation metrics
    'MustRuleComplianceMetric',
    'RejectPatternAvoidanceMetric',
    'HintGuidanceMetric',

    # Vegan compliance metrics (Issue #5)
    'VeganComplianceMetric',
    'AnimalProductDetector',
    'NaturalAcknowledgmentMetric',

    # Information security metrics
    'CastVisibilityMetric',
    'AdversarialLeakageDetector',
    'NaturalConversationMetric',

    # Exam security metrics
    'ExamAnswerProtectionMetric',
    'SuspiciousBehaviorDetectionMetric',
    'NeutralResponseMetric',
    'HintPreventionMetric',

    # Tool/Function schema security metrics
    'ToolSchemaProtectionMetric',
    'FunctionEnumerationPreventionMetric',
    'SchemaFormatLeakageMetric',
    'ToolProbeDetectionMetric',
    'ImplementationDetailsConcealmentMetric',
]