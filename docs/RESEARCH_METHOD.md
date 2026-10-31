# Research method

## Evidence labels

- **Physical:** directly observed on the owner-operated console; state exactly what was observed and any user-reported context.
- **Public source:** source code, official advisory, technical paper, or public documentation; state revision/date and whether primary.
- **Host test:** experiment on the Mac or another host; no target-system implication unless the same code is established.
- **Model/synthetic:** output of a model or synthetic input; supports only the model/tested parser.
- **Inference:** reasoned interpretation with premises and alternatives stated.
- **Unknown:** evidence is absent or insufficient.

## Minimum record

Every experiment needs a question, stop condition, target/environment version, tools and versions, exact steps, sanitized inputs/outputs, hashes where useful, interpretation, limitations, and independent review. Preserve raw logs when lawful, then scrub personal data before sharing. A hash preserves byte identity but does not prove device identity or legal provenance.

## Reachability test

For a candidate issue, document: (1) whether it is accessible in ordinary stock use; (2) whether unsigned code must already run; (3) the affected component/privilege boundary; (4) exact hardware and firmware evidence; (5) a safe reproduction path; (6) whether the result has independent confirmation. Findings requiring existing homebrew are not a first entry point.

## Stop criteria

Stop if the experiment would require modifying the console, accessing secrets, acquiring restricted artifacts, bypassing access controls, or sending malformed/destructive traffic. Stop a branch when repeated observations produce no new evidence relevant to pre-homebrew reachability.
