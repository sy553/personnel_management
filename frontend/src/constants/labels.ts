// 合同状态标签
export const CONTRACT_STATUS_LABELS = {
  active: '生效中',
  expired: '已到期',
  terminated: '已终止'
} as const

// 合同状态类型
export const CONTRACT_STATUS_TYPES = {
  active: 'success',
  expired: 'info',
  terminated: 'danger'
} as const

// 薪资变动类型标签
export const SALARY_CHANGE_LABELS = {
  promotion: '晋升调整',
  annual_adjustment: '年度调整',
  position_change: '岗位调动',
  other: '其他'
} as const

// 职位变动类型标签
export const POSITION_CHANGE_LABELS = {
  promotion: '晋升',
  transfer: '调动',
  demotion: '降职',
  adjustment: '调整'
} as const

// 职位变动类型样式
export const POSITION_CHANGE_TYPES = {
  promotion: 'success',
  transfer: 'warning',
  demotion: 'danger',
  adjustment: 'info'
} as const

// 文件类型标签
export const FILE_TYPE_LABELS = {
  pdf: 'PDF文件',
  doc: 'Word文档',
  docx: 'Word文档',
  xls: 'Excel表格',
  xlsx: 'Excel表格',
  jpg: '图片',
  jpeg: '图片',
  png: '图片'
} as const

// 文件类型样式
export const FILE_TYPE_STYLES = {
  pdf: 'primary',
  doc: 'primary',
  docx: 'primary',
  xls: 'success',
  xlsx: 'success',
  jpg: 'info',
  jpeg: 'info',
  png: 'info'
} as const

// 操作类型标签
export const OPERATION_TYPE_LABELS = {
  create: '新建',
  update: '修改',
  delete: '删除',
  download: '下载'
} as const

// 操作类型样式
export const OPERATION_TYPE_STYLES = {
  create: 'success',
  update: 'warning',
  delete: 'danger',
  download: 'info'
} as const 