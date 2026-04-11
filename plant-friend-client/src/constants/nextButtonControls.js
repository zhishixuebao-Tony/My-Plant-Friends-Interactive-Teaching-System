export const NEXT_BUTTON_KEYS = {
  welcome: 'welcome_next',
  sensory: 'sensory_submit_next',
  sensoryTransition: 'sensory_transition_next',
  viewRecordCards: 'view_record_cards_next',
  recordCard: 'record_card_submit_next',
  recordCardTransition: 'record_card_transition_next',
  resourcePack: 'resource_pack_next',
  finalDraft: 'final_draft_submit_next',
};

export const NEXT_BUTTON_LABELS = {
  [NEXT_BUTTON_KEYS.welcome]: '欢迎页 下一步',
  [NEXT_BUTTON_KEYS.sensory]: '观察页 提交并下一步',
  [NEXT_BUTTON_KEYS.sensoryTransition]: '观察过渡页 下一步',
  [NEXT_BUTTON_KEYS.viewRecordCards]: '查看记录卡页 下一步',
  [NEXT_BUTTON_KEYS.recordCard]: '新发现页 提交并下一步',
  [NEXT_BUTTON_KEYS.recordCardTransition]: '记录卡过渡页 下一步',
  [NEXT_BUTTON_KEYS.resourcePack]: '资源包页 下一步',
  [NEXT_BUTTON_KEYS.finalDraft]: '总结页 完成挑战',
};

export const DEFAULT_NEXT_BUTTON_CONTROL_STATE = Object.freeze({
  [NEXT_BUTTON_KEYS.welcome]: true,
  [NEXT_BUTTON_KEYS.sensory]: true,
  [NEXT_BUTTON_KEYS.sensoryTransition]: true,
  [NEXT_BUTTON_KEYS.viewRecordCards]: true,
  [NEXT_BUTTON_KEYS.recordCard]: true,
  [NEXT_BUTTON_KEYS.recordCardTransition]: true,
  [NEXT_BUTTON_KEYS.resourcePack]: true,
  [NEXT_BUTTON_KEYS.finalDraft]: true,
});
