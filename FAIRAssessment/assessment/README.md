# LINCS CFDE FAIR Assessment

This assessment builds off of the [C2M2 FAIR Assessment](https://github.com/nih-cfde/FAIR/tree/master/Demos/FAIRAssessment/c2m2). Instead of utilizing the DERIVA Client to query against data in the C2M2 model, we use the LDP3 JSON serialized metadata model. Some metrics were omitted which are completely uniform such as `Project Name`, and others were added including Gene & Drug ontological validation.

- [rubric.diff](./rubric.diff): Contains a diff between the C2M2 FAIR Assessment Rubric and this one.
- [rubric.py](./rubric.py): Contains the implemented rubric for this assessment.
- [dump.py](./dump.py): Can be used to extract an LDP3 metadata dump from the LDP3 API.
- [assess.py](./assess.py): Can be used to execute the assessment against a ldp3 metadata dump.
