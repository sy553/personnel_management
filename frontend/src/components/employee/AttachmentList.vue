<template>
  <div class="attachment-list">
    <el-descriptions :column="1" border>
      <template #title>
        <div class="section-title">
          <el-icon><Folder /></el-icon>
          附件资料
          <div class="upload-buttons" v-if="employeeStatus === 'active'">
            <el-button type="primary" link @click="handleUpload(false)">
              <el-icon><Upload /></el-icon>
              上传附件
            </el-button>
            <el-button type="primary" link @click="handleUpload(true)">
              <el-icon><Upload /></el-icon>
              批量上传
            </el-button>
          </div>
        </div>
      </template>
      <el-descriptions-item>
        <div v-if="attachments.length === 0" class="no-data">
          暂无附件资料
        </div>
        <el-table v-else :data="attachments" style="width: 100%">
          <el-table-column label="文件名称" min-width="200">
            <template #default="{ row }">
              <div class="file-name-cell">
                <el-icon :size="20" class="file-icon">
                  <component :is="getFileIcon(row.file_type)" />
                </el-icon>
                <span class="file-name">{{ row.file_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="file_size" label="文件大小" width="120">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column prop="upload_time" label="上传时间" width="180" />
          <el-table-column prop="uploader" label="上传人" width="120" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleDownload(row)">
                下载
              </el-button>
              <el-button type="primary" link @click="handlePreview(row)">
                预览
              </el-button>
              <el-button 
                type="danger" 
                link 
                @click="handleDelete(row)"
                v-if="employeeStatus === 'active'"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>
    </el-descriptions>

    <!-- 文件上传对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      :title="isBatchUpload ? '批量上传附件' : '上传附件'"
      width="550px"
      @close="handleUploadDialogClose"
    >
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :before-upload="beforeUpload"
        :on-progress="onUploadProgress"
        :on-success="onUploadSuccess"
        :on-error="onUploadError"
        :file-list="uploadFileList"
        :multiple="isBatchUpload"
        :limit="isBatchUpload ? 10 : 1"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 jpg、png、pdf、doc、docx、xls、xlsx 格式文件，单个文件不超过10MB
          </div>
        </template>
      </el-upload>
    </el-dialog>

    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="文件预览"
      width="80%"
      class="preview-dialog"
    >
      <div v-loading="previewLoading" class="preview-container">
        <template v-if="previewFile.file_type?.toLowerCase() === 'pdf'">
          <iframe
            v-if="previewUrl"
            :src="previewUrl"
            class="preview-pdf"
          ></iframe>
        </template>
        <template v-else-if="['jpg', 'jpeg', 'png'].includes(previewFile.file_type?.toLowerCase())">
          <img
            v-if="previewUrl"
            :src="previewUrl"
            class="preview-image"
            alt="预览图片"
          >
        </template>
        <div v-else class="preview-unsupported">
          该文件类型不支持预览
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Upload, UploadFilled, Document, Picture } from '@element-plus/icons-vue'
import type { UploadInstance, UploadProps, UploadUserFile } from 'element-plus'
import type { Attachment } from '@/types/employee'

interface Props {
  attachments: Attachment[]
  employeeStatus: 'active' | 'inactive'
  uploadUrl: string
  uploadHeaders: Record<string, string>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'add', files: File[]): void
  (e: 'delete', attachment: Attachment): void
  (e: 'preview', attachment: Attachment): void
  (e: 'download', attachment: Attachment): void
}>()

// 上传相关状态
const uploadRef = ref<UploadInstance>()
const uploadDialogVisible = ref(false)
const isBatchUpload = ref(false)
const uploadFileList = ref<UploadUserFile[]>([])

// 预览相关状态
const previewDialogVisible = ref(false)
const previewLoading = ref(false)
const previewFile = ref<Attachment>({} as Attachment)
const previewUrl = ref('')

// 处理上传按钮点击
const handleUpload = (batch: boolean) => {
  isBatchUpload.value = batch
  uploadDialogVisible.value = true
}

// 处理上传对话框关闭
const handleUploadDialogClose = () => {
  uploadRef.value?.clearFiles()
  uploadFileList.value = []
  isBatchUpload.value = false
}

// 处理文件上传前的验证
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isValidType = /\.(jpg|jpeg|png|pdf|doc|docx|xls|xlsx)$/i.test(file.name)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('文件格式不支持!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!')
    return false
  }
  return true
}

// 处理上传进度
const onUploadProgress: UploadProps['onProgress'] = (event, uploadFile) => {
  uploadFile.status = 'uploading'
}

// 处理上传成功
const onUploadSuccess: UploadProps['onSuccess'] = (response, uploadFile) => {
  if (response.code === 200) {
    uploadFile.status = 'success' as const
    ElMessage.success('上传成功')
    emit('add', [uploadFile.raw!])
  } else {
    uploadFile.status = 'fail' as const
    ElMessage.error(response.message || '上传失败')
  }
}

// 处理上传失败
const onUploadError: UploadProps['onError'] = (_, uploadFile) => {
  uploadFile.status = 'fail' as const
  ElMessage.error('文件上传失败，请稍后重试')
}

// 处理文件预览
const handlePreview = async (file: Attachment) => {
  previewFile.value = file
  previewLoading.value = true
  
  try {
    emit('preview', file)
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error('预览失败')
  } finally {
    previewLoading.value = false
  }
}

// 处理文件下载
const handleDownload = (file: Attachment) => {
  emit('download', file)
}

// 处理文件删除
const handleDelete = async (file: Attachment) => {
  try {
    await ElMessageBox.confirm('确定要删除该文件吗？', '提示', {
      type: 'warning'
    })
    emit('delete', file)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 获取文件图标
const getFileIcon = (fileType: string) => {
  const type = fileType.toLowerCase()
  if (['jpg', 'jpeg', 'png'].includes(type)) {
    return Picture
  }
  return Document
}

// 格式化文件大小
const formatFileSize = (size: number) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else {
    return (size / 1024 / 1024).toFixed(2) + ' MB'
  }
}
</script>

<style scoped>
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.upload-buttons {
  margin-left: auto;
  display: flex;
  gap: 12px;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #909399;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.preview-container {
  height: 600px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-pdf {
  width: 100%;
  height: 100%;
  border: none;
}

.preview-unsupported {
  text-align: center;
  color: #909399;
  padding: 20px;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-upload__tip) {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style> 