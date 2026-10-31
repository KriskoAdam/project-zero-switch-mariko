import json
from pathlib import Path
areas={
'formal_invariants':['resource_count_nonnegative','no_live_child_after_parent_close','unique_generation_tokens','rights_never_increase_without_grant','eventually_released_after_terminal_state'],
'state_machine':['reset_idempotence','close_idempotence','retry_idempotence','cancel_each_transition','reconnect_epoch_isolation'],
'ipc_contracts':['optional_field_default_equivalence','unknown_enum_rejection_consistency','field_order_independence','producer_consumer_schema_agreement','narrow_integer_roundtrip'],
'lifecycle':['duplicate_close_release_balance','transfer_owner_quota_conservation','allocation_failure_atomicity','stale_reply_cannot_mutate_new_session','cleanup_after_timeout'],
'differential':['versioned_model_invariant_preservation','parser_implementation_agreement','error_code_mapping_consistency','serialization_roundtrip','equivalent_sequence_state_equivalence'],
'arm64_semantics':['signed_extension_boundary_agreement','caller_callee_argument_roundtrip','condition_code_model_consistency','unaligned_access_model_policy','return_value_width_preservation'],
'compiler_binary':['optimization_invariant_preservation','dead_code_removal_semantics','relocation_target_consistency','symbol_alias_equivalence','instruction_decoder_fixture_agreement'],
'protocol_states':['duplicate_message_ordering','lost_ack_retry_state','reordered_independent_messages','sequence_number_wrap_model','partial_frame_recovery'],
'hardware_software_boundary':['clock_reset_epoch_consistency','shared_quota_boundary','power_loss_atomicity_model','dma_completion_order_model','device_reset_resource_reclamation'],
'emergent_combinations':['two_valid_ops_global_quota_violation','cross_service_partial_commit','independent_ops_commutativity','nested_transfer_close_race','error_cleanup_interleaving']}
items=[]
for area,claims in areas.items():
 for i,claim in enumerate(claims,1):
  title=claim.replace('_',' ')
  items.append({'id':f'{area[:3].upper()}-{i:02d}','area':area,'claim':f'In a synthetic contract model, test whether {title} holds under bounded inputs and operation interleavings.','test':f'Generate boundary values and bounded traces for {title}; compare against an independently implemented reference semantics.','falsifier':f'Find a valid generated input or trace where {title} is violated, then minimize and replay it.','testable':True,'synthetic_safe':True,'cross_discipline':area in ('emergent_combinations','hardware_software_boundary','compiler_binary'),'needs_target_artifact':False,'status':'untested_candidate'})
Path('PROJECT_ZERO/hypotheses/catalog.json').write_text(json.dumps(items,indent=2)+'\n')
