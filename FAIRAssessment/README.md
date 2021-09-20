# LINCS CFDE FAIR Assessment

This assessment builds off of the [C2M2 FAIR Assessment](https://github.com/nih-cfde/FAIR/tree/master/Demos/FAIRAssessment/c2m2). Instead of utilizing the DERIVA Client to query against data in the C2M2 model, we use the SigCom-LINCS JSON serialized metadata model. Some metrics were omitted which are out of scope like `Project Name`, while others were added including Gene & Drug ontological validation.

- [assessment/](./assessment): Contains the code to perform an automated FAIR assessment on SigCom-LINCS.
- [report/](./report): Shows a report with the results of the FAIR assessment of SigCom-LINCS contrasted against the C2M2 assessment in the CFDE.
