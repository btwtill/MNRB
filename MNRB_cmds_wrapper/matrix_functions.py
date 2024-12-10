import math
import maya.api.OpenMaya  as om #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class Matrix_functions():

    @staticmethod
    def getIdentityMatrix() -> list:
        identity_matrix = [1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000]
        return identity_matrix

    @staticmethod
    def flatToFourByFourMatrix(flat_matrix) -> list:
        matrix_four_by_four = [
            flat_matrix[0:4],
            flat_matrix[4:8],
            flat_matrix[8:12],
            flat_matrix[12:16]
        ]
        return matrix_four_by_four

    @staticmethod
    def normalize_row(row) -> list:
        length = math.sqrt(row[0]**2 + row[1]**2 + row[2]**2)
        return [value / length for value in row]
    
    @staticmethod
    def removeScaleFromMatrix(matrix) -> list:
        matrix_four_by_four = Matrix_functions.flatToFourByFourMatrix(matrix)

        matrix_four_by_four[0][:3] = Matrix_functions.normalize_row(matrix_four_by_four[0][:3])
        matrix_four_by_four[1][:3] = Matrix_functions.normalize_row(matrix_four_by_four[1][:3])
        matrix_four_by_four[2][:3] = Matrix_functions.normalize_row(matrix_four_by_four[2][:3])

        return [value for row in matrix_four_by_four for value in row]
    
    @staticmethod
    def setMatrixParentNoOffset(child, parent):
        MC.connectAttribute(parent, "worldMatrix[0]", child, "offsetParentMatrix")
        identity_matrix = Matrix_functions.getIdentityMatrix()
        MC.setObjectPositionMatrix(child, identity_matrix)

    @staticmethod
    def connectDecomposeToSRT(decompose_node, target_srt, translate = True, rotate = True, scale = True, rotate_order = True):
        for channel in "XYZ":
            if translate:
                MC.connectAttribute(decompose_node, "outputTranslate" + channel, target_srt, "translate" + channel)
            if rotate:
                MC.connectAttribute(decompose_node, "outputRotate" + channel, target_srt, "rotate" + channel)
            if scale:
                MC.connectAttribute(decompose_node, "outputScale" + channel, target_srt, "scale" + channel)

        if rotate_order:
                MC.connectAttribute(decompose_node, "inputRotateOrder", target_srt, "rotateOrder")

    @staticmethod
    def decomposeTransformWorldMatrix(source, rotate_order = True):
        decompose_node = MC.createDecomposeNode(source)
        MC.connectAttribute(source, "worldMatrix[0]", decompose_node, "inputMatrix")
        if rotate_order:
            MC.connectAttribute(source, "rotateOrder", decompose_node, "inputRotateOrder")

        return decompose_node

    @staticmethod
    def decomposeTransformWorldMatrixTo(source, target, rotate_order = True):
        decompose_node = Matrix_functions.decomposeTransformWorldMatrix(source, rotate_order = rotate_order)
        Matrix_functions.connectDecomposeToSRT(decompose_node, target, rotate_order = rotate_order)
        return decompose_node

    @staticmethod
    def connectSRTToCompose(source, compose_node, translate = True, rotate = True, scale = True, rotate_order = True):
        for channel in "XYZ":
            if translate:
                MC.connectAttribute(source, "translate" + channel, compose_node, "inputTranslate" + channel)
            if rotate:
                MC.connectAttribute(source, "rotate" + channel, compose_node, "inputRotate" + channel)
            if scale:
                MC.connectAttribute(source, "scale" + channel, compose_node, "inputScale" + channel)
        
        if rotate_order:
                MC.connectAttribute(source, "rotateOrder", compose_node, "inputRotateOrder")

    @staticmethod
    def disconnectSRTFromCompose(source, compose_node, translate = True, rotate = True, scale = True, rotate_order = True):
        for channel in "XYZ":
            if translate:
                MC.disconnectAttribute(source, "translate" + channel, compose_node, "inputTranslate" + channel)
            if rotate:
                MC.disconnectAttribute(source, "rotate" + channel, compose_node, "inputRotate" + channel)
            if scale:
                MC.disconnectAttribute(source, "scale" + channel, compose_node, "inputScale" + channel)
        
        if rotate_order:
                MC.disconnectAttribute(source, "rotateOrder", compose_node, "inputRotateOrder")

    @staticmethod
    def createComposeNodeFromTransformChannelbox(source, rotate_order = True, disconnect_from_source = True):
        compose_node = MC.createComposeNode(source)
        Matrix_functions.connectSRTToCompose(source, compose_node, rotate_order = rotate_order)
        if disconnect_from_source:
            Matrix_functions.disconnectSRTFromCompose(source, compose_node, rotate_order = rotate_order)
        return compose_node
    
    @staticmethod
    def connectOutputMatrixToOffsetParentMatrix(source, target, rotate_order = True):
        MC.connectAttribute(source, "outputMatrix", target, "offsetParentMatrix")
        if rotate_order:
            MC.connectAttribute(source, "inputRotateOrder", target, "rotateOrder")

    @staticmethod
    def setMatrixParentNoOffsetFromComposeNode(compose_node, child, rotate_order = True):
        Matrix_functions.connectOutputMatrixToOffsetParentMatrix(compose_node, child, rotate_order)
        MC.clearTransforms(child)

    @staticmethod
    def fillComposeMatrixNodeWithTransformationMatrix(compose_node, transformation_matrix, rotate_order = 0):
        translation = transformation_matrix.translation(om.MSpace.kWorld)
        rotation_rad = transformation_matrix.rotation(asQuaternion = False)
        rotation_deg = tuple(math.degrees(rotation) for rotation in rotation_rad)
        scale = transformation_matrix.scale(om.MSpace.kWorld)

        for index, channel in enumerate("XYZ"):
            MC.setAttribute(compose_node, "inputTranslate" + channel, translation[index])
            MC.setAttribute(compose_node, "inputRotate" + channel, rotation_deg[index])
            MC.setAttribute(compose_node, "inputScale" + channel, scale[index])

        MC.setAttribute(compose_node, "inputRotateOrder", rotate_order)

    @staticmethod
    def setMatrixParentWithOffset(child, parent, decompose_result = True):
        child_world_matrix = om.MMatrix(MC.getObjectWorldPositionMatrix(child))
        parent_world_matrix = om.MMatrix(MC.getObjectWorldPositionMatrix(parent))

        parent_world_matrix_inverse = parent_world_matrix.inverse()

        offset_matrix = parent_world_matrix_inverse * child_world_matrix
        offset_matrix_transformation = om.MTransformationMatrix(offset_matrix)

        offset_compose_node = MC.createComposeNode(child + "_parentOffset")
        Matrix_functions.fillComposeMatrixNodeWithTransformationMatrix(offset_compose_node, offset_matrix_transformation)

        offset_mult_matrix_node = MC.createMultMatrixNode(child + "_parentOffset")
        MC.connectAttribute(offset_compose_node, "outputMatrix", offset_mult_matrix_node, "matrixIn[0]")
        MC.connectAttribute(parent, "worldMatrix[0]", offset_mult_matrix_node, "matrixIn[1]")

        if decompose_result:
            offset_decompose_node = MC.createDecomposeNode(child + "_parentOffset")
            MC.connectAttribute(offset_mult_matrix_node, "matrixSum", offset_decompose_node, "inputMatrix")
            Matrix_functions.connectDecomposeToSRT(offset_decompose_node, child)
        else:
            MC.connectAttribute(offset_mult_matrix_node, "matrixSum", child, "offsetParentMatrix")
            MC.clearTransforms(child)
        print("Finished Matrix Parenting with Offset")
        return offset_compose_node, offset_mult_matrix_node

        



    