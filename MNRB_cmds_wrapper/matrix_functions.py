import math
import MNRB.MNRB_cmds_wrapper.cmds_wrapper as wrapper #type: ignore

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
        wrapper.MC.connectAttribute(parent, "worldMatrix[0]", child, "offsetParentMatrix")
        identity_matrix = Matrix_functions.getIdentityMatrix()
        wrapper.MC.setObjectPositionMatrix(child, identity_matrix)