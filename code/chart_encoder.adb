package body Chart_Encoder with SPARK_Mode is

   --  Ghost relational lemma: distinct (chart, rank) pairs have distinct
   --  global ranks, because the intervals [Base (K), Base (K) + Cells (K))
   --  are pairwise disjoint and consecutive.
   procedure Injectivity_Lemma
     (K1 : Chart_Id; R1 : Valid_Rank;
      K2 : Chart_Id; R2 : Valid_Rank) with
     Pre  => Natural (R1) < Cells (K1) and then Natural (R2) < Cells (K2)
               and then Base (K1) + Natural (R1) = Base (K2) + Natural (R2),
     Post => K1 = K2 and then R1 = R2
   is
   begin
      if K1 /= K2 then
         if K1 < K2 then
            --  Consecutive interval property:
            --  Base (K1) + Cells (K1) <= Base (K2)  (in fact = since consecutive,
            --  but <= suffices for disjointness of half-open intervals).
            pragma Assert
              (Base (K1) + Natural (R1) < Base (K1) + Cells (K1));
            for J in Chart_Id range K1 .. Chart_Id'Pred (K2) loop
               pragma Assert (Base (J) + Cells (J) <= Base (Chart_Id'Succ (J)));
            end loop;
            pragma Assert (Base (K1) + Cells (K1) <= Base (K2));
            pragma Assert (Base (K1) + Natural (R1) < Base (K2) + Natural (R2));
         else
            Injectivity_Lemma (K2, R2, K1, R1);
         end if;
      end if;
   end Injectivity_Lemma;

   function Encode (K : Chart_Id; R : Valid_Rank) return Address is
   begin
      pragma Assert (Natural (R) < Cells (K));
      pragma Assert (Base (K) + Natural (R) < Base (K) + Cells (K));
      pragma Assert (Base (K) + Cells (K) <= Arena_Size);
      pragma Assert (Base (K) + Natural (R) < Arena_Size);
      return Address (Base (K) + Natural (R));
   end Encode;

   procedure Decode
     (A : Address;
      K : out Chart_Id;
      R : out Valid_Rank)
   is
      N : constant Natural := Natural (A);
   begin
      if N < Base (Chart_Id'Val (1)) then
         K := Chart_Id'Val (0);
      elsif N < Base (Chart_Id'Val (2)) then
         K := Chart_Id'Val (1);
      else
         K := Chart_Id'Val (2);
      end if;
      R := Valid_Rank (N - Base (K));
      pragma Assert (Encode (K, R) = A);
   end Decode;

end Chart_Encoder;
