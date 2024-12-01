export interface Employee {
  employee_no: string
  name: string
  gender: string
  birth_date: string
  id_card: string
  phone: string
  email: string
  address: string
  department_id: number
  department?: Department
  position: string
  hire_date: string
  status: string
  education_history: EducationHistory[]
  work_experience: WorkExperience[]
  training_records: TrainingRecord[]
  position_changes: PositionChange[]
  reward_punishments: RewardPunishment[]
  contracts: Contract[]
  attachments: Attachment[]
  remarks?: string
}

export interface EducationHistory {
  id: number
  employee_no: string
  school: string
  major: string
  degree: string
  start_date: string
  end_date: string
  remarks?: string
}

export interface TrainingRecord {
  id: number
  employee_no: string
  training_name: string
  training_type: string
  start_date: string
  end_date: string
  trainer: string
  result: string
  remarks?: string
}

export interface WorkExperience {
  id: number
  employee_no: string
  company: string
  position: string
  start_date: string
  end_date: string
  description?: string
  remarks?: string
}

export interface PositionChange {
  id: number
  employee_no: string
  old_position: string
  new_position: string
  change_date: string
  change_reason: string
  remarks?: string
}

export interface RewardPunishment {
  id: number
  employee_no: string
  type: 'reward' | 'punishment'
  title: string
  description: string
  date: string
  amount?: number
  remarks?: string
}

export interface Attachment {
  id: number
  employee_no: string
  file_name: string
  file_path: string
  file_type: string
  upload_time: string
  description?: string
}

export interface Contract {
  id: number
  employee_no: string
  contract_type: string
  start_date: string
  end_date: string
  file_path: string
  status: string
  remarks?: string
}

export interface ContractForm {
  contract_type: string
  start_date: string
  end_date: string
  status: string
  remarks?: string
  file?: File
}

export interface Department {
  id: number
  name: string
  description?: string
}

export interface WorkInfo {
  department_id?: number
  position?: string
  hire_date?: string
  status?: string
  remarks?: string
} 