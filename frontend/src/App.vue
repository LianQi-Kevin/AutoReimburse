<script setup>
import {UploadFilled} from "@element-plus/icons-vue";
import { ElMessage } from 'element-plus'

const taxInfo = ref([])
// upload tax
function uploadSuccess(res, _, uploadFiles) {
    console.log(res)
    if (taxInfo.value.some(tax => tax["id"] === res.data["data"]["id"]) !== true){
        taxInfo.value.push(res.data["data"])
    } else {
        ElMessage.error(`id: ${res.data["data"]["id"]} 已上传`)
    }
}

function fileListRemove(uploadFile, uploadFiles) {
    console.log(uploadFile.name)

}

// info table
const multipleTableRef = ref()
const multipleSelection = ref([])
function handleSelectionChange(val) {
    multipleSelection.value = val
}

function toggleSelection(rows) {
    if (rows) {
        rows.forEach((row) => {
            multipleTableRef.value.toggleRowSelection(row, undefined)
        })
    } else {
        multipleTableRef.value.clearSelection()
    }
}

function deleteRow(index) {
    taxInfo.value.splice(index, 1)
}

</script>

<template>
    <div class="content">
        <div class="header">
            发票报销表生成器
        </div>
        <el-divider style="margin: 10px 0"/>
        <div class="item">
            <div class="upload">
                <el-scrollbar height="100%">
                    <el-upload
                    drag
                    multiple
                    class="uploadBox"
                    action="/apiDev/upload"
                    accept=".pdf, .png,.jpg,.jpeg,.jpe,.jp2,.bmp,.dib,.webp,.pbm,.pgm,.ppm,.pxm,.pnm,.tif,.tiff"
                    :on-success="uploadSuccess"
                    :on-remove="fileListRemove"
                >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                        拖拽或 <em>点击此处</em>上传发票文件
                    </div>
                    <template #tip>
                        <div class="el-upload__tip" style="margin-left: 5px">
                            仅支持 .pdf 或
                            <el-tooltip
                                effect="light"
                                placement="top"
                                content=".jpg, .jpeg, .jpe, .jp2, .bmp, .dib, .webp, .pbm, .pgm, .ppm, .pxm, .pnm, .tif, .tiff">
                                <el-text class="mx-1" type="primary">图片</el-text>
                            </el-tooltip>
                            文件
                        </div>
                    </template>
                </el-upload>
                </el-scrollbar>
            </div>
            <el-divider direction="vertical" style="height: 100%"/>
            <div class="infoAction">
                <el-scrollbar height="100%">
                    <el-table
                        ref="multipleTableRef"
                        :data="taxInfo"
                        stripe
                        style="width: 100%;"
                        table-layout="auto"
                        max-height="350px"
                        @selection-change="handleSelectionChange"
                    >
                        <el-table-column fixed type="selection" width="55" />
                        <el-table-column fixed prop="filename" label="文件名" />
                        <el-table-column prop="type" label="发票种类" />
                        <el-table-column prop="code" label="发票代码" />
                        <el-table-column prop="id" label="发票号码" />
                        <el-table-column prop="money" label="税后金额" />
                        <el-table-column prop="date" label="开票日期" />
                        <el-table-column prop="verify" label="校验码" />
                        <el-table-column fixed="right" label="操作" width="120">
                            <template #default="scope">
                                <el-button
                                    link
                                    type="primary"
                                    size="small"
                                    @click.prevent="deleteRow(scope.$index)"
                                >
                                    Remove
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                    <el-button-group style="margin-top: 20px; justify-self: left">
                        <el-button @click="toggleSelection()">Clear selection</el-button>
                        <el-button @click="toggleSelection()">Clear selection</el-button>
                    </el-button-group>
                </el-scrollbar>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
div.content {
    //background: #1D1E1F;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;

    div.header {
        margin: 5px 5px 0 20px;
        text-align: left;
        font-size: 25px;
    }
    div.item {
        display: flex;
        flex-direction: row;
        height: 100%;
        width: 100%;
        .upload {
            height: 100%;
            max-width: 300px;
            flex-grow: 1;
            .uploadBox {
                margin: 0 0 0 10px;
            }
        }
        .infoAction {
            height: 100%;
            max-width: 100%;
            flex-grow: 1;
        }
    }
}

.example-showcase .el-loading-mask {
    z-index: 9;
}
</style>
